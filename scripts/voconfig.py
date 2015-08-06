#!/usr/bin/python
import getopt
import sys
import re

#--- sub
def usage():
  print 'This program reads a table of VO data, and uses it to'
  print 'construct some products:'
  print '  - a users.conf file'
  print '  - a condor.conf file'
  print '  - a groups.conf file'
  print '  - a fragment of maui.conf file '
  print '  - a fragment of qmgr (pbs) conf file '
  print '  - a fragment of "site-info-def" with the'
  print '    QUEUES, VOS and LONG_GROUP_ENABLE variables.'
  print ''
  print 'The options to this program are:'
  print ' -c  --conf     <file>   conf file to read  (def: vo_data.conf)'
  print ' -s  --sidfrag  <file>   site-info.def frag (def: site-info.def.gen)'
  print ' -u  --users    <file>   users conf file    (def: users.conf.gen)'
  print ' -n  --condor   <file>   condor conf file    (def: condor.conf.gen)'
  print ' -g  --groups   <file>   groups conf        (def: groups.conf.gen)'
  print ' -a  --arguswn  <file>   arguswn conf       (def: arguswn.conf.gen)'
  print ' -m  --mauifrag <file>   maui frag          (def: maui.cfg.gen)'
  print ' -q  --qmgrfrag <file>   qmgr frag          (def: qmgr.conf.gen)'
  print ''

#--- sub
def initOptions(o):

  """ Sets the defaults and read the options """

  # Set defaults
  o['vo_data_file']      = 'vo_data.conf'
  o['sid_frag_file']     = 'site-info.def.gen'
  o['users_conf_file']   = 'users.conf.gen'
  o['condor_conf_file']  = 'condor.conf.gen'
  o['groups_conf_file']  = 'groups.conf.gen'
  o['arguswn_conf_file'] = 'arguswn.conf.gen'
  o['maui_frag_file']    = 'maui.cfg.gen'
  o['qmgr_frag_file']    =  'qmgr.conf.gen'
 
  # Read the options 
  try:
    options, remainder = getopt.getopt(sys.argv[1:], 'c:s:u:n:g:a:m:q:', [
      'conf=', 'sidfrag=', 'users=', 'condor=', 'groups=','arguswn=', 'mauifrag=','qmgrfrag='])

  except getopt.GetoptError:
    usage(); sys.exit(1)

  if len(options) <= 0:
    usage(); sys.exit(1)
 
  # Store the options 
  for opt, arg in options:
    if opt in ('-c', '--conf'):
      o['vo_data_file'] =  arg
    elif opt in ('-s', '--sidfrag'):
      o['sid_frag_file'] = arg
    elif opt in ('-u', '--users'):
      o['users_conf_file'] = arg
    elif opt in ('-n', '--condor'):
      o['condor_conf_file'] = arg
    elif opt in ('-g', '--groups'):
      o['groups_conf_file'] = arg
    elif opt in ('-a', '--arguswn'):
      o['arguswn_conf_file'] = arg
    elif opt in ('-m', '--mauifrag'):
      o['maui_frag_file'] = arg
    elif opt in ('-q', '--qmgrfrag'):
      o['qmgr_frag_file'] = arg
  
#--- class
class UsersConf:

  """ Produces a users.conf file """

  # Write the users.conf
  def write_users (self,vo_list,file,start_uid,start_add_uid):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open users.conf file '); sys.exit(1)

    # vouid - first UID in VO's range
    # voadduid - first UID in the additional range for VO
    vouid = start_uid
    voadduid = start_add_uid

    # For over the VOs
    for vo in vo_list:

      # Write block STD USERS
      nuid = vouid
      for jj in range(vo.users):
        record =  "%d:%s%03d:%d:%s:%s::\n" % (nuid, vo.name5, jj + 1, vo.gid,vo.name8,vo.name)
        match_obj = re.match('^DUMMY',vo.blockname)
        if match_obj is None:
          f.write(record)

        nuid = nuid + 1
    
      # Write block of PRODUCTION USERS
      nuid = vouid + 300
      n=vo.prd
      for jj in range(n ):
        record =  "%d:%s%02d:%d,%d:%s,%s:%s:%s:\n" % (nuid, 'prd' + vo.name3 , jj + 1, vo.pgid, vo.gid, vo.name5 + 'prd',vo.name8,vo.name,'prd')
        match_obj = re.match('^DUMMY',vo.blockname)
        if match_obj is None:
          f.write(record)
        nuid = nuid + 1

      # Write block of SGM USERS
      nuid = vouid + 400
      n=vo.sgm
      for jj in range(n ):
        record =  "%d:%s%02d:%d,%d:%s,%s:%s:%s:\n" % (nuid,'sgm' + vo.name3, jj + 1,vo.sgid,vo.gid,vo.name5 + 'sgm',vo.name8,vo.name,'sgm')
        match_obj = re.match('^DUMMY',vo.blockname)
        if match_obj is None:
          f.write(record)
        nuid = nuid + 1

      # Maybe write block of PILOT USERS (in additional range). Only happens if vo.pl > 0
      nuid = voadduid
      n= vo.pil
      for jj in range(n ):
        record =  "%d:%s%02d:%d,%d:%s,%s:%s:%s:\n" % (nuid,'pil' + vo.name3, jj + 1,vo.pilgid,vo.gid,vo.name5 + 'pil',vo.name8,vo.name,'pilot')
        match_obj = re.match('^DUMMY',vo.blockname)
        if match_obj is None:
          f.write(record)
        nuid = nuid + 1
    
      # set vouid and voadduid for next VO
      vouid = vouid + 500
      voadduid = voadduid + 250

    f.close()

#--- class
class CondorConf:

  """ Produces a condor.conf file """

  # Write the condor.conf
  def write_condor (self,vo_list,file):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open condor.conf file '); sys.exit(1)

    f.write('# Group names\n')
    f.write('GROUP_NAMES = \\\n')
    # 
    record =  "\tgroup_HIGHPRIO" 
    f.write(record + ',  \\\n')

    # For over the VOs
    for vo in vo_list:

      voName = re.sub(r"\.", "_", vo.name.upper())

      # Write generic group record
      record =  "\tgroup_%s" % (voName)
      match_obj = re.match('^DUMMY',vo.blockname)
      if match_obj is None:
        f.write(record + ',  \\\n')

     ## Write block STD USERS
     #record =  "\tgroup_%s.%s" % (voName, vo.name5)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore,  \\\n')
     #  f.write(record + '_score,  \\\n')
    
     ## Write block of PRODUCTION USERS
     #n=vo.prd
     #record =  "\tgroup_%s.%s" % (voName,'prd' + vo.name3)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore,  \\\n')
     #  f.write(record + '_score,  \\\n')

     ## Write block of SGM USERS
     #n=vo.sgm
     #record =  "\tgroup_%s.%s" % (voName,'sgm' + vo.name3)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore,  \\\n')
     #  f.write(record + '_score,  \\\n')

     ## Maybe write block of PILOT USERS (in additional range). Only happens if vo.pl > 0
     #n= vo.pil
     #record =  "\tgroup_%s.%s" % (voName,'pil' + vo.name3)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore,  \\\n')
     #  f.write(record + '_score,  \\\n')

    f.write('\n')
    f.close()

    try:
      f = open(file, 'a')
    except IOError:
      print('Cannot open condor.conf file '); sys.exit(1)

    f.write('# Fairshares\n')

    record =  "GROUP_QUOTA_DYNAMIC_group_HIGHPRIO  = 0.05\n"
    f.write(record + '\n')

    # For over the VOs
    for vo in vo_list:

      voName = re.sub(r"\.", "_", vo.name.upper())

      # Write generic group record
      record =  "GROUP_QUOTA_DYNAMIC_group_%s = %5.2f" % (voName, float(vo.arcquota))
      match_obj = re.match('^DUMMY',vo.blockname)
      if match_obj is None:
        f.write(record + '\n')

     ## Write block STD USERS
     #record =  "GROUP_QUOTA_DYNAMIC_group_%s.%s" % (voName, vo.name5)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore  = 0.1 \n')
     #  f.write(record + '_score  = 0.1 \n')
    
     ## Write block of PRODUCTION USERS
     #
     #record =  "GROUP_QUOTA_DYNAMIC_group_%s.%s" % (voName,'prd' + vo.name3)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore  = 0.1 \n')
     #  f.write(record + '_score  = 0.1 \n')

     ## Write block of SGM USERS
     
     #record =  "GROUP_QUOTA_DYNAMIC_group_%s.%s" % (voName,'sgm' + vo.name3)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore  = 0.1 \n')
     #  f.write(record + '_score  = 0.1 \n')

     ## Maybe write block of PILOT USERS (in additional range). Only happens if vo.pl > 0
     #record =  "GROUP_QUOTA_DYNAMIC_group_%s.%s" % (voName,'pil' + vo.name3)
     #match_obj = re.match('^DUMMY',vo.blockname)
     #if match_obj is None:
     #  f.write(record + '_mcore  = 0.1 \n')
     #  f.write(record + '_score  = 0.1 \n')

    f.write('\n')
    f.close()
    #---------------
    try:
      f = open(file, 'a')
    except IOError:
      print('Cannot open condor.conf file '); sys.exit(1)

    f.write('# Priority factors\n')

    record =  "DEFAULT_PRIO_FACTOR = 100000.00"
    f.write(record + '\n')
    record =  "GROUP_PRIO_FACTOR_group_HIGHPRIO  = 1.00\n"
    f.write(record + '\n')

    # For over the VOs
    for vo in vo_list:

      voName = re.sub(r"\.", "_", vo.name.upper())

      # Write generic group record
      record =  "GROUP_PRIO_FACTOR_group_%s = %5.2f" % (voName, 10000)
      match_obj = re.match('^DUMMY',vo.blockname)
      if match_obj is None:
        f.write(record + '\n')

    f.write('\n')
    f.close()


#--- class
class GroupsConf:

  """ Produces a groups.conf file """
  def __init__(self):
    x = 1

  # Write groups.conf
  def write_groups(self,vo_list,file):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open groups.conf file '); sys.exit(1)

    # Go over all the VOs
    for vo in vo_list:

      # Omit DUMMY...
      match_obj = re.match('^DUMMY',vo.blockname) 
      if match_obj is None:

        # Write this VO
        f.write('"/' + vo.name + '/sgm":::sgm:' + '\n')
        f.write('"/' + vo.name + '/lcgprod":::prd:' + '\n')
        f.write('"/' + vo.name + '/ROLE=lcgadmin":::sgm:' + '\n')
        f.write('"/' + vo.name + '/ROLE=production":::prd:' + '\n')

        # Maybe write pilots
        if re.match('yes',vo.pilot):
          f.write('"/' + vo.name + '/ROLE=pilot":::pilot:\n')

        f.write('"/' + vo.name + '"::::\n')
        f.write('"/' + vo.name + '/*"::::\n')
    f.close()

#--- class
class ArguswnConf:

  """ Produces a section of argus policy for the WNs """
  def __init__(self):
    x = 1

  # Write groups.conf
  def write_arguswn(self,vo_list,file):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open arguswn.conf file '); sys.exit(1)

    # Go over all the VOs
    for vo in vo_list:

      # Omit DUMMY...
      match_obj = re.match('^DUMMY',vo.blockname) 
      if match_obj is None:

        # Write this VO

        f.write('    rule permit {pfqan = "/' + vo.name + '\" }\n') 
        f.write('    rule permit {pfqan = "/' + vo.name + '/Role=lcgadmin\" }\n') 
        f.write('    rule permit {pfqan = "/' + vo.name + '/Role=production\" }\n') 

        # Maybe write pilots
        if re.match('yes',vo.pilot):
          f.write('    rule permit {pfqan = "/' + vo.name + '/Role=pilot\" }\n') 

    f.close()

#--- class
class Vo:

  """ Holds a list of VOs """

  # Constructor, with initial attribute values
  def __init__(self,fields):

    # Names, gids etc.

    self.blockname = fields[0]
    self.gid = int(fields[1])
    self.pgid = int(fields[2])
    self.sgid = int(fields[3])
    self.pilgid = int(fields[4])
    self.name = fields[5]
    self.name3 = fields[6]
    self.name5 = fields[7]
    self.name8 = fields[8]
    self.users = int(fields[9])
    self.prd = int(fields[10])
    self.sgm = int(fields[11])
    self.pil = int(fields[12])
    self.lcgadmin = fields[13]
    self.production = fields[14]
    self.pilot = fields[15]

    if ((re.match('^.*\d\d*$',self.name))      or
        (re.match('^.*\d\d*$',self.name3))     or
        (re.match('^.*\d\d*$',self.name5))     or
        (re.match('^.*\d\d*$',self.name8)) ):
      print('Warning: At least one of the name stubs of VO ' + self.blockname + ' has trailing digits' )

    if (self.lcgadmin != 'yes' and self.lcgadmin != 'no'):
      print('Warning: VO ' + self.blockname + ' has has bad value in lcgadmin field' )
    if (self.production != 'yes' and self.production != 'no'):
      print('Warning: VO ' + self.blockname + ' has has bad value in production field' )
    if (self.pilot != 'yes' and self.pilot != 'no'):
      print('Warning: VO ' + self.blockname + ' has has bad value in pilot field' )

    # Maui Fields

    self.mainUserFairShare = fields[16]
    self.mainUserPriority  = fields[17]
    self.prdUserFairShare = fields[18]
    self.prdUserPriority  = fields[19]
    self.sgmUserFairShare = fields[20]
    self.sgmUserPriority  = fields[21]
    self.pilotUserFairShare = fields[22]
    self.pilotUserPriority  = fields[23]

    # ARC fields
    self.arcquota = fields[24]

#--- class
class SidFrag:

  """ Produces the site-info.def fragment """

  # Write out the fragment of site-info.def
  def write_frag(self,vo_list,file):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open sid frag file'); sys.exit(1)

    f.write ('##############################\n')
    f.write ('# VO configuration variables #\n')
    f.write ('##############################\n')
    f.write ('\n')
    f.write ('QUEUES="long"\n')
    f.write ('\n')

    # Make the VOS= line
    vos_line = 'VOS="'
    for vo in vo_list:

      # Omit DUMMY...
      match_obj = re.match('^DUMMY',vo.blockname) 
      if match_obj is None:
        vos_line += vo.name
        vos_line += ' '
    vos_line += '"'
    f.write ( vos_line + '\n')
    f.write ( '\n')

    f.write ( 'LONG_GROUP_ENABLE="\\\n')

    # Go over all the VOs. The count var is to catch the last loop
    count = len(vo_list)
    for ii in range(0, count ):
      vo = vo_list[ii]

      # Omit DUMMY...
      if re.match('^DUMMY',vo.blockname):
        continue
      voms_rules = ' ' + vo.name 

      # Conditionally add roles
      if re.match('yes',vo.lcgadmin):
        voms_rules += ' /' + vo.name + '/ROLE=lcgadmin'
      if re.match('yes',vo.production):
        voms_rules += ' /' + vo.name + '/ROLE=production'
      if re.match('yes',vo.pilot):
        voms_rules += ' /' + vo.name + '/ROLE=pilot'

      # On all but last loop, end line with backslash, else double-quote
      if ii < count - 1:
        voms_rules += '\\'
      else: 
        voms_rules += '"'
      f.write ( voms_rules + '\n')

    f.write ('\n')
    f.close()

#--- class
class MauiFrag:

  """ Produces the maui.cfg fragment """

  # Write out the fragment of maui.cfg
  def write_frag(self,vo_list,file):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open maui frag file'); sys.exit(1)

    f.write ('##############################################\n')
    f.write ('# Fragment for sgm GROUPLIST.                #\n')
    f.write ('# You have to put it in the right            #\n')
    f.write ('# place and uncomment it.                    #\n')
    f.write ('#                                            #\n')
    f.write ('# Don\'t put more than about 254 chars here.  #\n')
    f.write ('##############################################\n')
    f.write ('\n')

    # GROUPLIST=atlassgm,alicesgm,babarsgm,calicsgm,cmssgm,dteamsgm,esrsgm,...
    groupListLine = '# GROUPLIST='

    for vo in vo_list:
      # Omit DUMMY...
      match_obj = re.match('^DUMMY',vo.blockname)
      if match_obj is None:
        newRecord =  "%s," % ( vo.name5 + 'sgm')
        myLen = len(groupListLine + newRecord)
        if (myLen < 254):
          groupListLine = groupListLine + newRecord

    # Get rid of trailing comma, just in case
    if (groupListLine[len(groupListLine)-1:] == ','):
      groupListLine = groupListLine[:len(groupListLine)-1]

    f.write(groupListLine + '\n')
    f.write('\n')
    f.write ('##############################################\n')
    f.write ('# Fragment for MAUI Configuration variables. #\n')
    f.write ('# You have to put it in the right place.     #\n')
    f.write ('##############################################\n')
    f.write ('\n')

    for vo in vo_list:

      # Omit DUMMY...
      match_obj = re.match('^DUMMY',vo.blockname)
      if match_obj is None:

        # mainUserFairShare, mainUserPriority , prdUserFairShare, prdUserPriority , sgmUserFairShare, sgmUserPriority , pilotUserFairShare, pilotUserPriority , 

        # Write block STD GROUP
        record =  "GROUPCFG[%s] \tFSTARGET=%s \tPRIORITY=%s\n" % ( vo.name8,vo.mainUserFairShare, vo.mainUserPriority)
        f.write(record)

        # Write block of PRODUCTION GROUP
        record =  "GROUPCFG[%s] \tFSTARGET=%s \tPRIORITY=%s\n" % ( vo.name5 + 'prd',vo.prdUserFairShare, vo.prdUserPriority)
        f.write(record)

        # Write block of SGM GROUP
        record =  "GROUPCFG[%s] \tFSTARGET=%s \tPRIORITY=%s\n" % ( vo.name5 + 'sgm',vo.sgmUserFairShare, vo.sgmUserPriority)
        f.write(record)

        # Maybe write PILOT GROUP
        if re.match('yes',vo.pilot):
          record =  "GROUPCFG[%s] \tFSTARGET=%s \tPRIORITY=%s\n" % ( vo.name5 + 'pil',vo.pilotUserFairShare, vo.pilotUserPriority)
          f.write(record)
        f.write('\n')
   

    f.close()

#--- class
class QmgrFrag:

  """ Produces the qmgr.conf fragment """

  # Write out the fragment of qmgr.conf
  def write_frag(self,vo_list,file):

    try:
      f = open(file, 'w')
    except IOError:
      print('Cannot open qmgr frag file'); sys.exit(1)

    f.write ('##############################################\n')
    f.write ('# Fragment for qmgr group acls.              #\n')
    f.write ('# You have to put it in the right            #\n')
    f.write ('# place.                                     #\n')
    f.write ('##############################################\n')
    f.write ('\n')
    #set queue long acl_groups = alice
    #set queue long acl_groups += alicesgm
    #set queue long acl_groups += aliceprd
    #set queue long acl_groups += atlas

    sep = '='

    for vo in vo_list:
      # Omit DUMMY...
      match_obj = re.match('^DUMMY',vo.blockname)
      if match_obj is None:

        # Write STD GROUP
        record =  "set queue long acl_groups %s %s\n" % ( sep,vo.name8)
        f.write(record)
        sep = '+='

        # Write PRODUCTION GROUP
        record =  "set queue long acl_groups %s %s\n" % ( sep,vo.name5 + 'prd')
        f.write(record)

        # Write SGM GROUP
        record =  "set queue long acl_groups %s %s\n" % ( sep,vo.name5 + 'sgm')
        f.write(record)

        # Maybe PILOT GROUP
        if re.match('yes',vo.pilot):
          record =  "set queue long acl_groups %s %s\n" % ( sep,vo.name5 + 'pil')
          f.write(record)

    f.close()

#--- class
class ConfReader:

  """ Reads the conf """

  # Constructor - set global values to null
  def __init__(self):
    self.start_uid = -1
    self.start_add_uid = -1

  # Read conf file
  def read_conf(self,vo_data_file,vo_list):

    # To find duplicate gids
    gidHash = {}

    # Conf file has several sections; 
    section = ''

    try:
      f = open(vo_data_file, 'r')
    except IOError:
      print('Cannot open input conf file'); sys.exit(1)

    # Read all the lines
    for line in f: 
      line = line.rstrip()
      line = re.sub('\#.*', '', line)

      # Omit blanks
      if re.match('^\s*$',line,0):
        continue

      # Track the section
      if re.match('^\s*\[general\]\s*$',line):
        section = 'general'
        continue
      if re.match('^\s*\[vos\]\s*$',line):
        section = 'vos'
        continue

      # Sorry - no unknown sections allowed.
      if (section != 'general')&(section != 'vos'):
        print('Odd conf file, check the section; is ' + section); sys.exit(1)

      if section == 'general':
        # Expect STARTUID and STARTADDUID in this section
        matchObj = re.match('STARTUID\=(.*)',line)
        if matchObj:
          self.start_uid = int(matchObj.group(1).strip())
        matchObj = re.match('STARTADDUID\=(.*)',line)
        if matchObj:
          self.start_add_uid = int(matchObj.group(1).strip())

      elif section == 'vos':
        # Expect VO lines in this section

        # Break up the fields
        fields = re.split('\s*,\s*',line)

        # Sorry - this line has the wrong number of fields 
        if (len(fields) != 25):
          print('Odd conf file, check the fields; line is ' + line); sys.exit(1)
        # Make a new VO with these fields, and stick it in the list
        newVo = Vo(fields)

        # Validate
        if newVo.gid in gidHash.keys():
          print('Odd conf file, duplicate gid, check the fields; line is ' + line); sys.exit(1)
        gidHash[newVo.gid] = 1; 

        if newVo.pgid in gidHash.keys():
          print('Odd conf file, duplicate pgid, check the fields; line is ' + line); sys.exit(1)
        gidHash[newVo.pgid] = 1; 

        if newVo.sgid in gidHash.keys():
          print('Odd conf file, duplicate sgid, check the fields; line is ' + line); sys.exit(1)
        gidHash[newVo.sgid] = 1; 

        if (newVo.pilgid in gidHash.keys() and (newVo.pilgid != -1)):
          print('Odd conf file, duplicate pilgid, check the fields; line is ' + line); sys.exit(1)
        gidHash[newVo.pilgid] = 1; 

        vo_list.append(newVo)

    f.close()
    # vo_list.sort(key=lambda x: x.blockname);

    # Sorry - the STARTUID, STARTADDUID and at least one VO are needed
    if (len(vo_list) <= 0):
      print('Odd conf file, no VOs found'); sys.exit(1)

    if (self.start_uid < 0  ):
      print('Odd conf file, no STARTUID found'); sys.exit(1)

    if (self.start_add_uid < 0  ):
      print('Odd conf file, no STARTADDUID found'); sys.exit(1)

    #-------------------------------------
    # Now check if overlap
    uidHash = {}

    vouid = self.start_uid
    voadduid = self.start_add_uid

    # For over the VOs
    for vo in vo_list:

      # STD USERS
      nuid = vouid
      for jj in range(vo.users):
        if nuid in uidHash.keys(): 
          print('Odd conf file, duplicate uid, check lines around vo ' + vo.name + '\n'); sys.exit(1)
        uidHash[nuid] = 1
        nuid = nuid + 1
    
      # PRODUCTION USERS
      nuid = vouid + 300
      for jj in range(vo.prd ):
        if nuid in uidHash.keys():
          print('Odd conf file, duplicate uid, check lines around vo ' + vo.name + '\n'); sys.exit(1)
        uidHash[nuid] = 1
        nuid = nuid + 1

      # SGM USERS
      nuid = vouid + 400
      for jj in range(vo.sgm ):
        if nuid in uidHash.keys():
          print('Odd conf file, duplicate uid, check lines around vo ' + vo.name + '\n'); sys.exit(1)
        uidHash[nuid] = 1
        nuid = nuid + 1

      # PILOT USERS 
      nuid = voadduid
      for jj in range(vo.pil ):
        if nuid in uidHash.keys():
          print('Odd conf file, duplicate uid, check lines around vo ' + vo.name + ' or the STARTADDUID variable\n'); sys.exit(1)
        uidHash[nuid] = 1
        nuid = nuid + 1
 
      # set vouid and voadduid for next VO
      vouid = vouid + 500
      voadduid = voadduid + 250

#--- main 

# Get the options

options = {} 
initOptions(options)

# Set up a ConfReader, and read the vo_list, start_uid, start_add_uid 

vo_list = []
conf_reader = ConfReader()
conf_reader.read_conf(options['vo_data_file'],vo_list)
start_uid = conf_reader.start_uid
start_add_uid = conf_reader.start_add_uid

# Set up a SidFrag, and write the fragment of site-info.def

sid_frag = SidFrag()
sid_frag.write_frag(vo_list,options['sid_frag_file'])

# Set up a UsersConf, and write the users.conf

users_conf = UsersConf()
users_conf.write_users(vo_list,options['users_conf_file'],start_uid,start_add_uid)

# Set up a CondorConf, and write the condor.conf

condor_conf = CondorConf()
condor_conf.write_condor(vo_list,options['condor_conf_file'])

# Set up a GroupsConf, and write the groups.conf

groups_conf = GroupsConf()
groups_conf.write_groups(vo_list,options['groups_conf_file'])

# Set up an Argus policy file for WNs

arguswn_conf = ArguswnConf()
arguswn_conf.write_arguswn(vo_list,options['arguswn_conf_file'])

# Set up a MauiFrag, and write the fragment of maui.cfg

maui_frag = MauiFrag()
maui_frag.write_frag(vo_list,options['maui_frag_file'])

# Set up a QmgrFrag, and write the fragment of qmgr.conf

qmgr_frag = QmgrFrag()
qmgr_frag.write_frag(vo_list,options['qmgr_frag_file'])


#--- end

