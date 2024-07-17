# coding:utf-8

from tools_hjh import Tools

date_str = Tools.locatdate().replace('-', '')

tables = '''
acct_facade.ap_processing_trans_detail where post_date >= date'2024-04-01' and post_date <= date'2024-07-02'
acct_facade.ap_processing_trans_data where batch_number >= date'2024-04-01' and batch_number <= date'2024-07-02'
'''


def main():
    script_str = ''

    script_str = script_str + '\n-- 目标端统计\n'
    for table_str in tables.strip().split('\n'):
        table_str = table_str.strip()
        owner = table_str.split('.')[0]
        table = table_str.split('.')[1].split(' where ')[0]
        where = table_str.split('.')[1].split(' where ')[1]
        script_str = script_str + 'select count(1) from ' + table_str + ';\n'
        
    tables_ = ''
    querys_ = ''        
    script_str = script_str + '\n-- 导出语句\n'
    for table_str in tables.strip().split('\n'):
        owner = table_str.split('.')[0]
        table = table_str.split('.')[1].split(' where ')[0]
        tables_ = tables_ + ',' + owner + '.' + table
        where = table_str.split('.')[1].split(' where ')[1]
        querys_ = querys_ + ',' + "" + owner + "." + table + ':"where ' + where + '''"'''
    tables_ = tables_.strip(',')
    querys_ = querys_.strip(',')

    dumpfile = 'expdp_ds_' + date_str + '_%U.dmp'
    directory = 'dump'
    tables__ = '(' + tables_ + ')'
    query = '(' + querys_ + ')'
    
    script_str = script_str + 'vim txt.par' + '\n'
    script_str = script_str + 'dumpfile=' + dumpfile + '\n'
    script_str = script_str + 'directory=' + directory + '\n'
    script_str = script_str + 'tables=' + tables__ + '\n'
    script_str = script_str + 'query=' + query + '\n'
    script_str = script_str + 'cluster=' + 'n' + '\n'
    script_str = script_str + 'parallel=' + '8' + '\n'
    script_str = script_str + 'compression=' + 'all' + '\n'
    script_str = script_str + 'expdp \\"/ as sysdba \\" parfile=txt.par' + '\n'
        
    script_str = script_str + '\n-- 导入语句\n'
    script_str = script_str + 'impdp \\"/ as sysdba \\" directory=dump dumpfile=expdp_ds_' + date_str + '_%U.dmp logfile=impdp_ds_' + date_str + '_.log cluster=n parallel=8 table_exists_action=append\n'
        
    script_str = script_str + '\n-- 删除语句\n'
    for table_str in tables.strip().split('\n'):
        owner = table_str.split('.')[0]
        table = table_str.split('.')[1].split(' where ')[0]
        where = table_str.split('.')[1].split(' where ')[1]
        script_str = script_str + 'delete from ' + table_str + ';\n'
        
    script_str = script_str + '\n-- scp语句 64.3操作\n'
    script_str = script_str + 'scp oracle@11.111.28.107:/dbbak/dump/expdp_ds_' + date_str + '_*.dmp /tmp\n'
    script_str = script_str + 'scp /tmp/expdp_ds_' + date_str + '_*.dmp oracle@11.111.24.149:/dbbak/dump\n'
    script_str = script_str + 'scp -P 7859 /dbbak/dump/expdp_ds_' + date_str + '_*.dmp oracle@14.32.5.1:/localdisk/dump\n'

    print(script_str)

    
if __name__ == '__main__':
    main()
