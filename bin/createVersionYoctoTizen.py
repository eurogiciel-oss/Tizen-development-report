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
Created on  29 spt. 2014

@author: ronan@fridu.net
'''
try:
    import cmdln
except:
    print >> sys.stderr, 'Error spec2yocto require "python-cmdln" please install it.'
    sys.exit( 1 )
    
import sys
    
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def cleanYoctoVer(s):
  return s.split(":")[-1]

def isNewerRev(src_rev, cnd_rev):
  splited_src=src_rev.split(".")
  splited_cnd=cnd_rev.split(".")
  for i in range(len(splited_src)):
    if i < len(splited_cnd):
      v_src=splited_src[i].split("+")[0].split("git")[0].split("p")[0].split("a")[0].split("_")[0].split("r")[0].split("c")[0].split("-")[0]
      c_src=splited_cnd[i].split("+")[0].split("git")[0].split("p")[0].split("a")[0].split("_")[0].split("r")[0].split("c")[0].split("-")[0]
      
      if is_number(v_src) and is_number(c_src):
        if int(v_src) > int(c_src) :
          return True
        elif int(v_src) < int(c_src) :
          return False 
  return False

def getYoctoMax(listVer):
  if len(listVer) == 0:
    return "None"
  
  ver="0.0.0"
  for v in listVer:
    if isNewerRev(v,ver):
      ver=v
  return ver

     
class CreateVersionYoctoTizen(cmdln.Cmdln):
    name = "createVersionYoctoTizen" 
    version = "0.1"
    
    @cmdln.option( "--ImagePackagesList",
                  action = "store",
                  default = "listImagePackage.txt",
                  help = "the Tizen rpm source file\n #./listYoctoImagePackage.sh ${project_path} > listImagePackage.txt \nDefault: listImagePackage.txt" )
    @cmdln.option( "--TizenSRC",
                  action = "store",
                  default = "Tizen-rpm-source.html",
                  help = "the Tizen rpm source file\n #wget http://download.tizen.org/snapshots/tizen/ivi/latest/repos/atom/source/ -O Tizen-rpm-source.html \nDefault: Tizen-rpm-source.html" )
    @cmdln.option( "--YoctoSRC",
                  action = "store",
                  default = "Yocto-recipes-source.txt",
                  help = "select the project.\n #bitbake-layers show-recipes > Yocto-recipes-source.txt \nDefault: Yocto-recipes-source.txt" )
    @cmdln.option( "--YoctoSRC_ignored",
                  action = "store",
                  default = "meta-tizen",
                  help = "ignore src for meta \nDefault: meta-tizen" )
    @cmdln.option( "--manifest_fix_result",
                  action = "store",
                  default = "manifest_fix_result.txt",
                  help = "manifest_fix_result" )
    @cmdln.option( "--recipes_path",
                  action = "store",
                  default = "recipes_path.txt",
                  help = "recipes_path" )
    @cmdln.option( "--pkg_Tizen_update",
                  action = "store",
                  default = "pkg_Tizen_update.txt",
                  help = "pkg_Tizen_update" )
    def do_status(self, subcmd, opts): 
        """generate status
        
        ${cmd_usage}--
        ${cmd_option_list}
        """
        yoctoVerFile = open(opts.YoctoSRC,"r")

        l_line=[]
        for line in yoctoVerFile:
            line = line.replace("\n","")
            l_line.append(line)
        yoctoVerFile.close()
        
        i=0
        yoctoPkg= {}
        while( i< len(l_line)-1 ):
            if not l_line[ i ].startswith("  ") and len(l_line[ i ]) > 1 :
                pkg_name=l_line[ i ].split(":")[0]
                i+=1
                yoctoPkg[pkg_name]=[]
                while(i< len(l_line)-1 and l_line[ i ].startswith("  ")  ):
                    #print pkg_name,l_line[ i ].split()
                    meta=l_line[ i ].split()[0]
                    version=l_line[ i ].split()[1]
                    if opts.YoctoSRC_ignored not in meta:
                        yoctoPkg[pkg_name].append(cleanYoctoVer(version))
                    i+=1
            else:
                i+=1
                
        tizenVerFile = open(opts.TizenSRC,"r")
        tizenPkg={}
        for line in tizenVerFile:
            line = line.replace("\n","")
            if ".src.rpm" in line:
                rpm_name=line.split(".src.rpm</a>")[0].split(".src.rpm\">")[1]
                release=rpm_name[rpm_name.rfind("-")+1:]
                rpm_name=rpm_name[:rpm_name.rfind("-")]
                version=rpm_name[rpm_name.rfind("-")+1:]
                name=rpm_name[:rpm_name.rfind("-")]
                tizenPkg[name]=version 
        tizenVerFile.close()
   
        imagePkg={}
        for imagePackagesPath in opts.ImagePackagesList.split(","):
            imagePackagesListFile= open(imagePackagesPath,"r")
            imageYoctoPkg_version={}
            for line in imagePackagesListFile:
                line = line.replace("\n","")
                rpm_name=line.split(".src.rpm")[0]
                release=rpm_name[rpm_name.rfind("-")+1:]
                rpm_name=rpm_name[:rpm_name.rfind("-")]
                version=rpm_name[rpm_name.rfind("-")+1:]
                name=rpm_name[:rpm_name.rfind("-")]
            
                if version =="git" and release =="r0":
                    imagePkg[name]='Tizen'
                else:
                    imagePkg[name]='Yocto'
                    imageYoctoPkg_version[name]=version
                
            imagePackagesListFile.close()
        
        reviewPkg={}
        manifest_fix_resultFile = open(opts.manifest_fix_result,"r")
        for line in manifest_fix_resultFile:
            line = line.replace("\n","")
            pkg_name,review_url,review_status=line.split(" ")
            reviewPkg[pkg_name]=[review_url,review_status]
            
        manifest_fix_resultFile.close()
        
        pkg_recipes_path_dico={}
        pkg_recipes_pathFile = open(opts.recipes_path,"r")
        for line in pkg_recipes_pathFile:
            line = line.replace("\n","")
            pkg_name,recipes_path=line.split("\t")
            pkg_recipes_path_dico[pkg_name]=recipes_path
        pkg_recipes_pathFile.close()
        
        pkg_jira_update={}

        jira_updateFile = open(opts.pkg_Tizen_update,"r")
        for line in jira_updateFile:
	    if '\t' in line:
                line = line.replace("\n","")
                pkg_name,jira=line.split("\t")
                pkg_jira_update[pkg_name]=jira
        jira_updateFile.close()
        
        resList=imagePkg.keys()
        resList.sort()
        for k in resList:
          if k in tizenPkg.keys(): 
            tizenV=tizenPkg[k]
          else:
            tizenV="None"

          if k in imageYoctoPkg_version.keys() :
            yoctoV=imageYoctoPkg_version[k]
          else:
            if k in yoctoPkg.keys():
              yoctoV=getYoctoMax(yoctoPkg[k])
            else:
              yoctoV="None"
          
          revision_status=""
          if yoctoV == "None":
              revision_status="-"
          elif tizenV == "None":
              revision_status="-"
          elif tizenV == yoctoV:
              revision_status="sync"
          elif isNewerRev(tizenV , yoctoV):
              revision_status="newer"
          else :
              revision_status="older"
              
          review_status=" "
          review_url=" "
          if k in reviewPkg.keys():
              [review_url,review_status]=reviewPkg[k]
              
          jira=" "
          if k in pkg_jira_update.keys():
              jira="https://bugs.tizen.org/jira/browse/"+pkg_jira_update[k]
          
          pkg_recipes_path = " "
          if k in pkg_recipes_path_dico.keys():
              pkg_recipes_path=pkg_recipes_path_dico[k]
              
          print "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % (k, imagePkg[k], tizenV, yoctoV, revision_status,review_url,review_status,jira,pkg_recipes_path)


def main():
    createVersionYoctoTizen = CreateVersionYoctoTizen()
    sys.exit( createVersionYoctoTizen.main() )
    
    
if __name__ == '__main__':
    main()
