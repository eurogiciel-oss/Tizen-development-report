#!/usr/bin/python
#
# Copyright 2014, Intel Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# native

'''
Created on  13 oct. 2014

@author: ronan.lemartret@open.eurogiciel.org
'''
try:
    import cmdln
except:
    print >> sys.stderr, 'Error spec2yocto require "python-cmdln" please install it.'
    sys.exit( 1 )
    
import sys
import os

#TODO need precision
#WARNING if patch can be a gz file
#WARNING if patch can be conpose by many commit
def isPatch(files) :
    return (".diff" in files) or (".patch" in files)

#TODO need precision
def isFromIntel(patch_file) :
    if patch_file.endswith('.diff') or patch_file.endswith('.patch'):
      with open(patch_file,"r") as patch_fd:
        for line in patch_fd:
          if line.startswith("From:") and (("intel.com" in line) or ("eurogiciel.org" in line)):
            return True
    return False
  

def count_intel_patch(SRCDIR,package_files):
    count_intel_patch=0
    for p in package_files:
      if isPatch( p) and isFromIntel(os.path.join(SRCDIR,p)):
       count_intel_patch+=1
    return count_intel_patch

def count_patch(package_files) :
    count_patch=0
    for p in package_files:
      if isPatch( p):
       count_patch+=1
    return count_patch

#What if many spec file?
def get_license(SRCDIR,package_files) :
    license=""
    for p in package_files:
      if (".spec" in p):
       return find_license(os.path.join(SRCDIR,p))
    return license

#What if many license file?
#TODO need precision
def find_license(spec_file) :
  license=""
  with open(spec_file,"r") as spec_fd:
    for line in spec_fd:
      if "License:" in line:
          return line.split("License:")[1].replace("\n","").replace("\t","").replace(" ","")
  return license

class CheckRpmSrc(cmdln.Cmdln):
    name = "createVersionYoctoTizen" 
    version = "0.1"
    
    @cmdln.option( "--rpmsSRCDIR",
                  action = "store",
                  default = "Tizen-rpm-source.html",
                  help = "the Tizen rpms source dir" )
    def do_status(self, subcmd, opts): 
        """generate status
        
        ${cmd_usage}--
        ${cmd_option_list}
        """
        for package_rpm in os.listdir(opts.rpmsSRCDIR):
            package_dir=package_rpm
            release=package_rpm[package_rpm.rfind("-")+1:].replace(".src.rpm","")
            package_rpm=package_rpm[:package_rpm.rfind("-")]
            version=package_rpm[package_rpm.rfind("-")+1:]
            name=package_rpm[:package_rpm.rfind("-")]
            package_files = os.listdir(os.path.join(opts.rpmsSRCDIR, package_dir))
            nb_patch=count_patch(package_files)
            license=get_license(os.path.join(opts.rpmsSRCDIR, package_dir),package_files)
            nb_intel_patch=count_intel_patch(os.path.join(opts.rpmsSRCDIR, package_dir),package_files)
            
            print "%s\t%s\t%s\t%s\t%s" %(name, version, license, nb_patch, nb_intel_patch)
        
        
def main():
    checkRpmSrc = CheckRpmSrc()
    sys.exit( checkRpmSrc.main() )
    
if __name__ == '__main__':
    main()