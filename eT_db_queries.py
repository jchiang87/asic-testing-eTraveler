import os
import MySQLdb

def nullFunc(*args):
    return None

class Database(object):
    def __init__(self, pars):
        self.pars = pars
    def apply(self, sql, args=None, cursorFunc=nullFunc):
        sql = sql.replace('?', '%s')
        my_connection = MySQLdb.connect(**self.pars)
        cursor = my_connection.cursor()
        try:
            if args is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, args)
            results = cursorFunc(cursor)
        except MySQLdb.DatabaseError, message:
            cursor.close()
            my_connection.close()
            raise MySQLdb.DatabaseError, message
        cursor.close()
        if cursorFunc is nullFunc:
            my_connection.commit()
        my_connection.close()
        return results

summary_md = [('read_noise', ('read_noise',)),
              ('flat_pairs', ('full_well',)),
              ('flat_pairs', ('max_frac_dev',)),
              ('cte', ('cti_high_serial', 'cti_high_serial_error',)),
              ('cte', ('cti_low_serial', 'cti_low_serial_error',)),
              ('cte', ('cti_high_parallel', 'cti_high_parallel_error',)),
              ('cte', ('cti_low_parallel', 'cti_low_parallel_error',)),
              ('bright_defects', ('bright_pixels',)),  # int
              ('dark_defects', ('dark_pixels',)),  # int
              ('bright_defects', ('bright_columns',)),  # int
              ('dark_defects', ('dark_columns',)),  # int
              ('traps', ('num_traps',)),  # int
              ('dark_current', ('dark_current_95CL',)),
              ('qe_analysis', ('band', 'QE')), # int, float
              ('prnu', ('wavelength', 'pixel_stdev', 'pixel_mean')), # int, float, float
              ('fe55_analysis', ('psf_sigma',))]

pars = dict(read_default_file=os.path.join(os.environ['HOME'], '.my.cnf_eT'))
db = Database(pars)
values = lambda curs : [x for x in curs]

# Pick a sensor:
sensor = 'e2v-CCD250-11093-10-04'
process_name = 'test_report_offline'

# Find all activities with test reports
sql = """select act.id, act.parentActivityId from Activity act 
    join Hardware hw on act.hardwareId=hw.id 
    join Process pr on act.processId=pr.id 
    join ActivityStatusHistory statusHist on act.id=statusHist.activityId
    where statusHist.activityStatusId=1 
    and hw.lsstId='%(sensor)s' 
    and pr.name='%(process_name)s'
    order by act.parentActivityId desc""" % locals()
sql = ' '.join(sql.split())
print sql
results = db.apply(sql, cursorFunc=values)
print results
parentActivityId = [x[1] for x in results][0]
print parentActivityId
print

for schemaName, names in summary_md[:7]:
    for resultName in names:
        sql = """select res.schemaInstance, res.value 
             from FloatResultHarnessed res 
             join Activity act on res.activityId=act.id
             where res.schemaName='%(schemaName)s'
             and res.name='%(resultName)s'
             and act.parentActivityId=%(parentActivityId)s""" % locals()
        sql = ' '.join(sql.split())
        print sql
        results = db.apply(sql, cursorFunc=values)
        for row in results:
            print row
        print



