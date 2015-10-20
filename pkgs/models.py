import os
import sys
import logging
import shutil
import subprocess
import plistlib
import optparse
import fnmatch
import time

from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)

APPNAME = settings.APPNAME
DEFAULT_MAKECATALOGS = settings.DEFAULT_MAKECATALOGS
REPO_DIR = settings.MUNKI_REPO_DIR
GIT_BRANCHING = settings.GIT_BRANCHING
GIT_IGNORE_PKGS = settings.GIT_IGNORE_PKGS
PRODUCTION_BRANCH = settings.PRODUCTION_BRANCH
MUNKI_PKG_ROOT = settings.MUNKI_PKG_ROOT

def fail(message):
    sys.stderr.write(message)
    sys.exit(1)

def execute(command):    
    popen = subprocess.Popen(command, stdout=subprocess.PIPE)
    lines_iterator = iter(popen.stdout.readline, b"")
    for line in lines_iterator:
        print(line) # yield line

usage = "%prog [options]"
o = optparse.OptionParser(usage=usage)

o.add_option("--makecatalogs", default=DEFAULT_MAKECATALOGS,
    help=("Path to makecatalogs. Defaults to '%s'. "
              % DEFAULT_MAKECATALOGS))

opts, args = o.parse_args()

MAKECATALOGS = opts.makecatalogs

try:
    GIT = settings.GIT_PATH
except:
    GIT = None

class MunkiPkgGit:
    """A simple interface for some common interactions with the git binary"""
    cmd = GIT
    args = []
    results = {}

    @staticmethod
    def __chdirToMatchPath(aPath):
        """Changes the current working directory to the same parent directory as
        the file specified in aPath. Example:
        "/Users/Shared/munki_repo/pkgsinfo/app/FredsApp-1.0.0.plist" would change
        directories to "/Users/Shared/munki_repo/pkgsinfo/app" """
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
        self.checkoutProductionBranch()
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

    def commitFileAtPathForCommitter(self, aPath, committer):
        """Commits the file(s) at 'aPath'. This method will also automatically
        generate the commit log appropriate for the status of aPath where status
        would be 'modified', 'new file', or 'deleted'"""
        branch_name = None
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
        pkgsinfo_path = os.path.join(REPO_DIR, 'pkgsinfo')
        itempath = aPath
        if aPath.startswith(pkgsinfo_path):
            itempath = aPath[len(pkgsinfo_path):]

        # If Git branching is enabled, create a new branch
        if GIT_BRANCHING:
            branch_name = self.checkoutUserBranch(committer)

        # generate the log message - would be good to pass details of each file
        # maybe we can get it from the status message - return it to views.py?
        # In the meantime, we just log the author and that it's a Munki-Do run
        # log_msg = ('%s %s pkginfo file \'%s\' via %s'
        #            % (author_name, action, itempath, APPNAME))
        log_msg = ('makecatalogs run at %s by %s via %s' % (aPath, author_name, APPNAME))
        
        # commit
        self.runGit(['commit', '-m', log_msg, '--author', author_info])
        if self.results['returncode'] != 0:
            logger.info("Failed to commit changes to %s" % aPath)
            logger.info("This was the error: %s" % self.results['output'])
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
            else:
                logger.info("Pushed changes to %s" % aPath)

        # If Git branching is enabled, return to master branch
        if GIT_BRANCHING:
            self.checkoutProductionBranch()
        return 0

    def addFileAtPathForCommitter(self, aPath, aCommitter):
        """Commits a file to the Git repo."""
        self.__chdirToMatchPath(aPath)
        self.runGit(['add', aPath])
        # Let's just do one commit when everything's added. That is set during
        # makecatalogs so no need to do it here
        #  if self.results['returncode'] == 0:
        #      self.commitFileAtPathForCommitter(aPath, aCommitter)

    def addMakeCatalogsForCommitter(self, aCommitter):
        """Commits the updated catalogs to the Git repo."""
        catalogs_path = os.path.join(REPO_DIR, 'catalogs')
        self.__chdirToMatchPath(catalogs_path)
        self.runGit(['add', catalogs_path])
        # Let's just do one commit when everything's added.
        if self.results['returncode'] == 0:
            self.commitFileAtPathForCommitter(catalogs_path, aCommitter)

    def deleteFileAtPathForCommitter(self, aPath, aCommitter):
        """Deletes a file from the filesystem and Git repo."""
        self.__chdirToMatchPath(aPath)
        self.runGit(['rm', aPath])
        logger.info("Performed 'git rm' on %s" % aPath)
        # Let's just do one commit when everything's added. That is set during
        # makecatalogs so no need to do it here
        #  if self.results['returncode'] == 0:
        #      self.commitFileAtPathForCommitter(aPath, aCommitter)



# Read contents of all pkginfo files. This is done by reading the contents of catalogs/all

class Packages(object):
    @classmethod
    def detail(self, findtext):
        '''Returns a list of available pkgs, which is a list
        of pkg names (strings)'''
        all_catalog_path = os.path.join(REPO_DIR, 'catalogs/all')
        if os.path.exists(all_catalog_path):
            try:
                all_catalog_items = plistlib.readPlist(all_catalog_path)
                all_catalog_items = sorted(all_catalog_items, key=lambda x: (x['name'].lower(), x['version']))
                index = 0
                for item in all_catalog_items:
                    item['index'] = index
                    index += 1
                if findtext:
                    filtered_list = []
                    for item in all_catalog_items:
                        if fnmatch.fnmatch(item['name'].lower(), findtext.lower()):
                            filtered_list.append(item)
                    return filtered_list
                else:
                    return all_catalog_items
            except Exception, errmsg:
                return None
        else:
            return None

    @classmethod
    def orphaned(self):
        '''Returns a list of orphaned pkg files where pkginfo files have been removed'''
        all_catalog_path = os.path.join(REPO_DIR, 'catalogs/all')
        all_pkgs = []
        if os.path.exists(all_catalog_path):
            try:
                all_catalog_items = plistlib.readPlist(all_catalog_path)
                for item in all_catalog_items:
                    item_location = os.path.join(MUNKI_PKG_ROOT, item['installer_item_location'])
                    all_pkgs.append(item_location)
            except OSError as e: 
                logger.info("Error: %s" % (e))
                return None
            logger.info("all_pkgs:\n%s" % (all_pkgs))
            orphaned_pkgs = []
            for root, dirs, files in os.walk(MUNKI_PKG_ROOT, topdown=False):
                for name in files:
                    pkg_fullpath = os.path.join(os.path.join(root, name))
                    pkg_location = pkg_fullpath.lstrip(MUNKI_PKG_ROOT)
                    pkg_location.lstrip('/')
                    if pkg_fullpath not in all_pkgs:
                        orphaned_pkgs.append(pkg_location)
                        logger.info("Orphaned pkg found: %s" % (pkg_location))
                    else:
                        # TEMP DEBUG ONLY
                        logger.info("Non-orphaned pkg found: %s" % (pkg_location))
            return orphaned_pkgs
        else:
            return None

    @classmethod
    def move(self, pkg_name, pkg_version, pkg_catalog, committer):
        '''Rewrites the catalog of the selected pkginfo files. Adapted from grahamgilbert/munki-trello'''
        done = False
        for root, dirs, files in os.walk(os.path.join(REPO_DIR,'pkgsinfo'), topdown=False):
            for name in files:
                # Try, because it's conceivable there's a broken / non plist
                plist = None
                try:
                    plist = plistlib.readPlist(os.path.join(root, name))
                except:
                    pass
                if plist and plist['name'] == pkg_name and plist['version'] == pkg_version:
                    plist['catalogs'] = [pkg_catalog]
                    plistlib.writePlist(plist, os.path.join(root, name))
                    if GIT:
                        git = MunkiPkgGit()
                        git.addFileAtPathForCommitter(os.path.join(root, name), committer)
                    done = True
                    break
            if done:
                break

    @classmethod
    def add(self, pkg_name, pkg_version, pkg_orig, pkg_catalog, committer):
        '''Appends the catalog of the selected pkginfo files.'''
        done = False
        for root, dirs, files in os.walk(os.path.join(REPO_DIR,'pkgsinfo'), topdown=False):
            for name in files:
                plist = None
                # Try, because it's conceivable there's a broken / non plist
                try:
                    plist = plistlib.readPlist(os.path.join(root, name))
                except:
                    pass
                if plist and plist['name'] == pkg_name and plist['version'] == pkg_version:
                    # Check that the catalog is not already in this plist
                    if pkg_catalog not in plist['catalogs']:
                        plist['catalogs'].append(pkg_catalog)
                        plistlib.writePlist(plist, os.path.join(root, name))
                        if GIT:
                            git = MunkiPkgGit()
                            git.addFileAtPathForCommitter(os.path.join(root, name), committer)
                    done = True
                    break
            if done:
                break

    @classmethod
    def remove(self, pkg_name, pkg_version, pkg_orig, committer):
        '''Removes the selected catalog from the pkginfo files.'''
        done = False
        for root, dirs, files in os.walk(os.path.join(REPO_DIR,'pkgsinfo'), topdown=False):
            for name in files:
                # Try, because it's conceivable there's a broken / non plist
                plist = None
                try:
                    plist = plistlib.readPlist(os.path.join(root, name))
                except:
                    pass
                if plist and plist['name'] == pkg_name and plist['version'] == pkg_version:
                    current_catalogs = plist['catalogs']
                    # Try to remove this catalog from the array if it exists
                    try:
                        plist['catalogs'].remove(pkg_orig)
                    except:
                        pass
                    plistlib.writePlist(plist, os.path.join(root, name))
                    if GIT:
                        git = MunkiPkgGit()
                        git.addFileAtPathForCommitter(os.path.join(root, name), committer)
                    done = True
                    break
            if done:
                break

    @classmethod
    def delete_pkgs(self, pkg_name, pkg_version, committer):
        '''Deletes a package and its associated pkginfo file, then induces makecatalogs'''
#        logger.info("pkg_name: %s; pkg_version: %s" % (pkg_name, pkg_version))
        done_delete = False
        for root, dirs, files in os.walk(os.path.join(REPO_DIR,'pkgsinfo'), topdown=False):
            for name in files:
                # Try, because it's conceivable there's a broken / non plist
                plist = None
                try:
                    plist = plistlib.readPlist(os.path.join(root, name))
                except:
                    pass
                if plist and plist['name'] == pkg_name and plist['version'] == pkg_version:
                    pkg_to_delete = plist['installer_item_location']
                    logger.info("name: %s; pkg_to_delete: %s; root: %s" % (name, pkg_to_delete, root))
                    if not GIT:
                        try:
                            os.remove(os.path.join(root, name))
                        except OSError as e:
                            logger.info("This failed to delete: %s" % (name))
                            logger.info("The error message was: %s" % (e))
                        try:
                            os.remove(os.path.join(MUNKI_PKG_ROOT,pkg_to_delete))
                        except OSError as e:
                            logger.info("This failed to delete: %s" % (name))
                            logger.info("The error message was: %s" % (e))
                    else:
                        git = MunkiPkgGit()
                        git.deleteFileAtPathForCommitter(os.path.join(root, name), committer)
                        if not GIT_IGNORE_PKGS:
                            git.deleteFileAtPathForCommitter(
                                    os.path.join(MUNKI_PKG_ROOT,pkg_to_delete), committer)
                        elif GIT_BRANCHING:
                            # If we're not git'ting packages but we're branching git, we
                            # shouldn't allow the packages to actually be deleted!
                            # Makecatalogs will still remove the plists from munki catalogs.
                            # Admin will have to manually remove packages :(
                            logger.info("Not deleting since GIT_BRANCHING is enabled: %s" % (pkg_to_delete))
                        else:
                            # If we're not branching then everyone is on the master branch so 
                            # can also delete the packages
                            try:
                                os.remove(os.path.join(MUNKI_PKG_ROOT,pkg_to_delete))
                            except OSError as e:
                                logger.info("This failed to delete: %s" % (pkg_to_delete))
                                logger.info("The error message was: %s" % (e))
                    done_delete = True
                    break
            if done_delete:
                break

    @classmethod
    def getGitBranch(self):
        """Returns the current branch"""
        pkgsinfo_path = os.path.join(REPO_DIR, 'pkgsinfo')
        git = MunkiPkgGit()
        git.gitPull(pkgsinfo_path)
        current_branch = git.getCurrentBranch(pkgsinfo_path)
        return current_branch

    @classmethod
    def gitPull(self):
        """Performs git pull"""
        pkgsinfo_path = os.path.join(REPO_DIR, 'pkgsinfo')
        git = MunkiPkgGit()
        git.gitPull(pkgsinfo_path)

    @classmethod
    def makecatalogs(self, committer):
        task = execute([MAKECATALOGS, REPO_DIR])
        if GIT:
            git = MunkiPkgGit()
            git.addMakeCatalogsForCommitter(committer)

    @classmethod
    def delete_orphaned_pkg(self, pkg_to_delete, committer):
        '''Deletes a package, then induces makecatalogs if not set to ignore pkgs'''
        if not GIT_IGNORE_PKGS:
            git = MunkiPkgGit()
            git.deleteFileAtPathForCommitter(
                                    os.path.join(MUNKI_PKG_ROOT,pkg_to_delete), committer)
        else:
            try:
                os.remove(os.path.join(MUNKI_PKG_ROOT,pkg_to_delete))
            except OSError as e:
                logger.info("This failed to delete: %s" % (pkg_to_delete))
                logger.info("The error message was: %s" % (e))


class Pkgs(models.Model):
    class Meta:
        permissions = (("can_view_pkgs", "Can view packages"),)