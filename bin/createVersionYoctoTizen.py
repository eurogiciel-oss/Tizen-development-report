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
                  default = "Yocot-recipes-source.txt",
                  help = "select the project.\n #bitbake-layers show-recipes > Yocot-recipes-source.txt \nDefault: Yocot-recipes-source.txt" )
    @cmdln.option( "--YoctoSRC_ignored",
                  action = "store",
                  default = "meta-tizen",
                  help = "ignore src for meta \nDefault: meta-tizen" )
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
        
        imagePackagesListFile= open(opts.ImagePackagesList,"r")
        imagePkg={}
        imagePkg_version={}
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
                imagePkg_version[name]=version
        imagePackagesListFile.close()
        
        resList=imagePkg.keys()
        resList.sort()
        for k in resList:
          if k in tizenPkg.keys(): 
            tizenV=tizenPkg[k]
          else:
            tizenV="None"
          
          if k in yoctoPkg.keys():
            yoctoV=getYoctoMax(yoctoPkg[k])
          else:
            if k in imagePkg_version.keys() :
              yoctoV=imagePkg_version[k]
            else:
              yoctoV="None"
          
          status=""
          if yoctoV == "None":
              status="-"
          elif tizenV == "None":
              status="-"
          elif tizenV == yoctoV:
              status="sync"
          elif isNewerRev(tizenV , yoctoV):
              status="newer"
          else :
              status="older"
              
          print "%s\t%s\t%s\t%s\t%s" % (k, imagePkg[k], tizenV, yoctoV, status)


def main():
    createVersionYoctoTizen = CreateVersionYoctoTizen()
    sys.exit( createVersionYoctoTizen.main() )
    
    
if __name__ == '__main__':
    main()