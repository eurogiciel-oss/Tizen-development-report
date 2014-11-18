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
import sys
import os

try:
    import cmdln
except:
    print >> sys.stderr, 'Error spec2yocto require "python-cmdln" please install it.'
    sys.exit( 1 )
    
import shlex, subprocess


class CheckReview(cmdln.Cmdln):
    name = "CheckReview" 
    version = "0.1"
    
    @cmdln.option( "--manifest_fix",
                  action = "store",
                  default = "manifest_fix.xml",
                  help = "the Tizen manifest fix file" )
    def do_status(self, subcmd, opts): 
        """generate status
        
        ${cmd_usage}--
        ${cmd_option_list}
        """
        package_dico= {}
        
        manifest_fixFile = open(opts.manifest_fix,"r")
        
        for line in manifest_fixFile:
            line = line.replace("\n","")
            if ("<!--" in line) and ("https://review.tizen.org/gerrit/" in line ):
                res_name,res_id=line.split("https://review.tizen.org/gerrit/")
                if "-->" in res_id:
                    res_id=res_id.split("-->")[0].replace(" ","")
                if res_id.endswith("/"):
                    res_id=res_id[:-1]
                if "/" in res_id:
                    res_id=res_id[res_id.rfind("/")+1:]
                    
                if "<!--" in res_name:
                    res_name=res_name.split("<!--")[1].replace(" ","")
                    
                cmd_status = "ssh review.tizen.org gerrit query  \"change:%s\"" % (res_id)
                args = shlex.split(cmd_status)
                
                res_status=""
                res_cmd_status = subprocess.check_output(args)
                for line in res_cmd_status.split("\n"):
                    if "status:" in line: 
                        res_status=line.split("status:")[1].replace(" ","")
                        
                        break
                    
                print "%s https://review.tizen.org/gerrit/%s %s" % (res_name,res_id,res_status)
    
def main():
    checkReview = CheckReview()
    sys.exit( checkReview.main() )
    
if __name__ == '__main__':
    main()