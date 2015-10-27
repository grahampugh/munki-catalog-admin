import os
import shutil
import logging
import subprocess
import plistlib
import time

from django.conf import settings
from django.db import models

from catalogs.models import Catalog

logger = logging.getLogger(__name__)

USERNAME_KEY = settings.MANIFEST_USERNAME_KEY
APPNAME = settings.APPNAME
REPO_DIR = settings.MUNKI_REPO_DIR
ALL_ITEMS = settings.ALL_ITEMS
GIT_BRANCHING = settings.GIT_BRANCHING
PRODUCTION_BRANCH = settings.PRODUCTION_BRANCH
MANIFEST_RESTRICTION_KEY = settings.MANIFEST_RESTRICTION_KEY


try:
    GIT = settings.GIT_PATH
except:
    GIT = None

class MunkiGit:
    """A simple interface for some common interactions with the git binary"""
    cmd = GIT
    args = []
    results = {}

    @staticmethod
    def __chdirToMatchPath(aPath):
        """Changes the current working directory to the same parent directory as
        the file specified in aPath. Example:
        "/Users/Shared/munki_repo/manifests/CoolManifest" would change
        directories to "/Users/Shared/munki_repo/manifests" """
        os.chdir(os.path.dirname(aPath))

    def runGit(self, customArgs=None):
        """Executes the git command with the current set of arguments and
        returns a dictionary with the keys 'output', 'error', and
        'returncode'. You can optionally pass an array into customArgs to
        override the self.args value without overwriting them."""
        customArgs = self.args if customArgs == None else customArgs
        proc = subprocess.Popen([self.cmd] + customArgs,
                                shell=False,
                                bufsize=-1,
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        (output, error) = proc.communicate()
        self.results = {"output": output, 
                       "error": error, "returncode": proc.returncode}
        return self.results

    def pathIsRepo(self, aPath):
        """Returns True if the path is in a Git repo, false otherwise."""
        self.__chdirToMatchPath(aPath)
        self.runGit(['status', aPath])
        return self.results['returncode'] == 0

    def gitPull(self, aPath):
        """Does a git pull!"""
        self.__chdirToMatchPath(aPath)
        self.runGit(['pull'])

    def getCurrentBranch(self, aPath):
        """Returns the current branch"""
        self.__chdirToMatchPath(aPath)
        self.runGit(['rev-parse', '--abbrev-ref', 'HEAD'])
        return self.results['output']

    def checkoutUserBranch(self, committer):
        """Creates a new git branch with name_timestamp"""
        time_stamp = str(time.strftime('%Y%m%d%H%M%S'))
        branch_committer = str(committer)
        seq = (branch_committer, time_stamp)
        s = "_"
        branch_name = s.join(seq)
        logger.info("Branch name: %s" % branch_name)
        self.runGit(['checkout', '-b', branch_name])
        if self.results['returncode'] != 0:
            logger.info("Failed to checkout to branch %s" % (time_stamp, branch_name))
            logger.info("This was the error: %s" % self.results['output'])
        else:
#            self.runGit(['push', '--set-upstream', 'origin', branch_name])
            logger.info("Checked out branch %s" % branch_name)
            return branch_name

    def checkoutProductionBranch(self):
        """Checkout the master/production branch"""
        self.runGit(['checkout', PRODUCTION_BRANCH])
        if self.results['returncode'] != 0:
            logger.info("Failed to change branches to %s" % PRODUCTION_BRANCH)
            logger.info("This was the error: %s" % self.results['output'])
        else:
            self.runGit(['pull'])
#            self.runGit(['push', '--set-upstream' 'origin', PRODUCTION_BRANCH])
            logger.info("Checked out branch %s" % PRODUCTION_BRANCH)

    def checkoutCustomBranch(self, branch_name):
        """Checkout an existing branch - used for new manifests"""
        self.runGit(['checkout', branch_name])
        if self.results['returncode'] != 0:
            logger.info("Failed to change branches to %s" % branch_name)
            logger.info("This was the error: %s" % self.results['output'])
        else:
            self.runGit(['pull'])
#            self.runGit(['push', '--set-upstream' 'origin', branch_name])
            logger.info("Checked out branch %s" % branch_name)

    def commitFileAtPathForCommitter(self, aPath, branch_name, committer):
        """Commits the file at 'aPath'. This method will also automatically
        generate the commit log appropriate for the status of aPath where status
        would be 'modified', 'new file', or 'deleted'"""
        self.__chdirToMatchPath(aPath)
        # get the author information
        author_name = committer.first_name + ' ' + committer.last_name
        author_name = author_name if author_name != ' ' else committer.username
        author_email = (committer.email or 
                        "%s@munki-do" % committer.username)
        author_info = '%s <%s>' % (author_name, author_email)
        # Pre-configure git - required because Bitbucket ignores the --author flag
        self.runGit(['config', 'user.email', author_email])
        self.runGit(['config', 'user.name', author_name])

        # get the status of the file at aPath
        statusResults = self.runGit(['status', aPath])
        statusOutput = statusResults['output']
        if statusOutput.find("new file:") != -1:
            action = 'created'
        elif statusOutput.find("modified:") != -1:
            action = 'modified'
        elif statusOutput.find("deleted:") != -1:
            action = 'deleted'
        else:
            action = 'did something with'

        # determine the path relative to REPO_DIR for the file at aPath
        manifests_path = os.path.join(REPO_DIR, 'manifests')
        itempath = aPath
        if aPath.startswith(manifests_path):
            itempath = aPath[len(manifests_path):]

        # generate the log message
        log_msg = ('%s %s manifest \'%s\' via %s'
                  % (author_name, action, itempath, APPNAME))
        
        # commit
        self.runGit(['commit', '-m', log_msg, '--author', author_info])
        if self.results['returncode'] != 0:
            logger.info("Failed to commit changes to %s" % aPath)
            logger.info("This was the error: %s" % self.results['output'])
            return -1
        else:
            logger.info("Committed changes to %s" % aPath)
            # if git branching enabled, we need to push to the correct branch
            if branch_name:
                self.runGit(['push', '--set-upstream', 'origin', branch_name])
            else:
                self.runGit(['push'])
            if self.results['returncode'] != 0:
                logger.info("Failed to push changes to %s" % aPath)
                logger.info("This was the error: %s" % self.results['output'])
                return -1
            else:
                logger.info("Pushed changes to %s" % aPath)
                logger.info("This was the output: %s" % self.results['output'])

        # If Git branching is enabled, return to master branch
        if GIT_BRANCHING:
            self.checkoutProductionBranch()
        return 0
        

    def addFileAtPathForCommitter(self, manifest, aPath, aCommitter):
        """Adds a file to the Git repo, then commits it."""
        self.__chdirToMatchPath(aPath)
        
        # If Git branching is enabled, create a new branch, or 
        # if a new manifest already set, checkout the branch already defined
        if GIT_BRANCHING:
            if 'new_manifest' in manifest:
                if manifest['new_manifest'] == 'new':
                    branch_name = self.checkoutUserBranch(aCommitter)
                    manifest['new_manifest'] = branch_name
                else:
                    branch_name = manifest['new_manifest']
                    self.checkoutCustomBranch(branch_name)
                    del manifest['new_manifest']
            else:
                branch_name = self.checkoutUserBranch(aCommitter)
        else:
            branch_name = None
        try:
            plistlib.writePlist(manifest, aPath)
            logger.info("Wrote plist at %s" % (aPath))
        except Exception, errmsg:
            logger.info("Failed to write plist at %s" % (aPath))
            logger.info("manifest contents: %s" % (manifest))
            pass
        # don't commit if a new manifest has just been created and git branching is enabled
        if not 'new_manifest' in manifest:
            self.runGit(['add', aPath])
            if self.results['returncode'] == 0:
                self.commitFileAtPathForCommitter(aPath, branch_name, aCommitter)
        return 0


    def deleteFileAtPathForCommitter(self, aPath, aCommitter):
        """Deletes a file from the filesystem and Git repo."""
        self.__chdirToMatchPath(aPath)

        # If Git branching is enabled, create a new branch
        if GIT_BRANCHING:
            branch_name = self.checkoutUserBranch(aCommitter)
        else:
            branch_name = None

        self.runGit(['rm', aPath])
        if self.results['returncode'] == 0:
            self.commitFileAtPathForCommitter(aPath, branch_name, aCommitter)
        return 0


def trimVersionString(version_string):
    ### from munkilib.updatecheck
    """Trims all lone trailing zeros in the version string after major/minor.

    Examples:
      10.0.0.0 -> 10.0
      10.0.0.1 -> 10.0.0.1
      10.0.0-abc1 -> 10.0.0-abc1
      10.0.0-abc1.0 -> 10.0.0-abc1
    """
    if version_string == None or version_string == '':
        return ''
    version_parts = version_string.split('.')
    # strip off all trailing 0's in the version, while over 2 parts.
    while len(version_parts) > 2 and version_parts[-1] == '0':
        del(version_parts[-1])
    return '.'.join(version_parts)

class Manifest(object):
    @staticmethod
    def __pathForManifestNamed(aManifestName):
        '''Returns the path to a manifest given the manifest's name'''
        return os.path.join(
            REPO_DIR, 'manifests', aManifestName.replace(':', '/'))

    @classmethod
    def list(cls):
        '''Returns a list of available manifests'''
        manifests_path = os.path.join(REPO_DIR, 'manifests')
        manifests = []
        skipdirs = ['.svn', '.git', '.AppleDouble']
        for dirpath, dirnames, filenames in os.walk(manifests_path):
            for skipdir in skipdirs:
                if skipdir in dirnames:
                    dirnames.remove(skipdir)
            subdir = dirpath[len(manifests_path):]
            for name in filenames:
                if name.startswith('.'):
                    # don't process these
                    continue
                manifests.append(os.path.join(subdir, name).lstrip('/'))
        return manifests

    @classmethod
    def new(cls):
        '''Returns an empty manifest object'''
        manifest = {}
        for section in ['catalogs', 'included_manifests', 'managed_installs',
                        'managed_uninstalls', 'managed_updates',
                        'optional_installs']:
            manifest[section] = []
        if MANIFEST_RESTRICTION_KEY:
            manifest[MANIFEST_RESTRICTION_KEY] = []
        manifest['new_manifest'] = 'new'
        logger.info("New manifest: %s" % manifest)
        return manifest

    @classmethod
    def read(cls, manifest_name):
        '''Gets the contents of a manifest'''
        manifest_path = cls.__pathForManifestNamed(manifest_name)
        if os.path.exists(manifest_path):
            try:
                return plistlib.readPlist(manifest_path)
            except Exception, errmsg:
                return {}
        else:
            return {}

    @classmethod
    def write(cls, manifest_name, manifest, committer):
        '''Writes a changed manifest to disk'''
        # muck about with the username
        if '_user_name' in manifest:
            user_list = manifest['_user_name']
            if user_list:
                manifest[USERNAME_KEY] = user_list[0]
            del manifest['_user_name']
        # attempt to prevent Manifest.write turning the restriction key into a list
        manifest_path = cls.__pathForManifestNamed(manifest_name)
        if not GIT:
            try:
                plistlib.writePlist(manifest, manifest_path)
            except Exception, errmsg:
                pass
        elif GIT:
                git = MunkiGit()
                git.addFileAtPathForCommitter(manifest, manifest_path, committer)
            # need to deal with errors

    @classmethod
    def delete(cls, manifest_name, committer):
        '''Deletes a manifest from the disk'''
        manifest_path = cls.__pathForManifestNamed(manifest_name)
        if not os.path.exists(manifest_path):
            print "Unable to find manifest to delete '%s'" % manifest_path
            return -1
        if not GIT:
            os.remove(manifest_path)
        else:
            git = MunkiGit()
            git.deleteFileAtPathForCommitter(manifest_path, committer)
    
    @classmethod
    def copy(cls, manifest_name, manifest_copy):
        manifest_name = cls.__pathForManifestNamed(manifest_name)
        manifest_copy = cls.__pathForManifestNamed(manifest_copy)
        print manifest_name
        print manifest_copy

        if not os.path.exists(manifest_name):
            print "Unable to find manifest to copy '%s'" % manifest_name
            return -1

        if not os.path.exists(manifest_copy):
            shutil.copy(manifest_name, manifest_copy)

    @classmethod
    def getInstallItemNames(cls, manifest_name):
        '''Returns a dictionary containing types of install items
        valid for the current manifest'''
        suggested_set = set()
        update_set = set()
        versioned_set = set()
        manifest = cls.read(manifest_name)
        if manifest:
            if ALL_ITEMS:
                catalog_list = ['all']
            else:
                catalog_list = manifest.get('catalogs', ['all'])
            for catalog in catalog_list:
                catalog_items = Catalog.detail(catalog)
                if catalog_items:
                    suggested_names = list(set(
                        [item['name'] for item in catalog_items
                         if not item.get('update_for')]))
                    suggested_set.update(suggested_names)
                    update_names = list(set(
                        [item['name'] for item in catalog_items
                         if item.get('update_for')]))
                    update_set.update(update_names)
                    item_names_with_versions = list(set(
                        [item['name'] + '-' + 
                        trimVersionString(item['version'])
                        for item in catalog_items]))
                    versioned_set.update(item_names_with_versions)
        return {'suggested': list(suggested_set),
                'updates': list(update_set),
                'with_version': list(versioned_set)}

    @classmethod
    def findUserForManifest(cls, manifest_name):
        '''returns a username for a given manifest name'''
        if USERNAME_KEY:
            return cls.read(manifest_name).get(USERNAME_KEY, '')

    @classmethod
    def getGitBranch(self):
        """Returns the current branch"""
        manifests_path = os.path.join(REPO_DIR, 'manifests')
        git = MunkiGit()
        git.gitPull(manifests_path)
        current_branch = git.getCurrentBranch(manifests_path)
        return current_branch

    @classmethod
    def gitPull(self):
        """Performs git pull"""
        manifests_path = os.path.join(REPO_DIR, 'manifests')
        git = MunkiGit()
        git.gitPull(manifests_path)


class Manifests(models.Model):
    class Meta:
            permissions = (("can_view_manifests", "Can view manifests"),)