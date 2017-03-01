# create_datastax_opscenter_login
- '-U','--username', help='login to be created',required=False
- '-D','--dropfirst', help='drop user if exists',required=False, default='False'
- '-R','--role', help='role of user being added',required=False, default='readonly'
- '-M','--send_email', help='send email with credentials',required=False, default='True'
- '-S','--server', help='opscenter host server',required=False, default='xx'
