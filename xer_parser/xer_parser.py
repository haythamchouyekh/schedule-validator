import pandas as pd

class Activity:
    def __init__(self):
        self.task_id       = ""
        self.task_code     = ""
        self.task_name     = ""
        self.duration      = 0.0
        self.remaining_dur = 0.0
        self.total_float   = 0.0
        self.free_float    = 0.0
        self.start         = ""
        self.finish        = ""
        self.act_start     = ""
        self.act_finish    = ""
        self.constraint    = ""
        self.constraint2   = ""
        self.wbs_id        = ""
        self.calendar_id   = ""
        self.task_type     = ""
        self.status_code   = ""
        self.proj_id       = ""
        self.successors    = []
        self.predecessors  = []

class Relationship:
    def __init__(self):
        self.pred_task_id = ""
        self.succ_task_id = ""
        self.pred_type    = ""
        self.lag          = 0.0

class XERParser:
    def __init__(self, filepath):
        self.filepath      = filepath
        self.activities    = {}
        self.relationships = []
        self.dataframes    = {}

    def parse(self):
        self._read_xer_file()
        self._parse_activities()
        self._parse_relationships()
        self._link_relationships()
        if 'PROJECT' in self.dataframes and 'proj_short_name' in self.dataframes['PROJECT'].columns:
            print(f"[✔] Projects found:")
            print(self.dataframes['PROJECT']['proj_short_name'].to_string())
        print(f"[✔] Parsed {len(self.activities)} activities and {len(self.relationships)} relationships.")

    def _read_xer_file(self):
        tables        = {}
        current_table = None
        columns       = None
        try:
            with open(self.filepath, 'r', encoding='latin-1') as file:
                for line in file:
                    line = line.strip()
                    if line.startswith('%T'):
                        current_table = line.split('\t')[1].strip()
                        tables[current_table] = []
                        continue
                    if line.startswith('%F') and current_table:
                        columns = line.split('\t')[1:]
                        continue
                    if current_table and columns and (line.startswith('%R') or not line.startswith('%')):
                        data = line.split('\t')[1 if line.startswith('%R') else 0:]
                        pad  = [None] * max(0, len(columns) - len(data))
                        tables[current_table].append(dict(zip(columns, data[:len(columns)] + pad)))
        except UnicodeDecodeError as e:
            print(f"[✘] Encoding error: {e}")
            return
        target_tables = ['PROJECT', 'TASK', 'TASKPRED', 'CALENDAR', 'PROJWBS']
        for table, rows in tables.items():
            if table in target_tables and rows:
                self.dataframes[table] = pd.DataFrame(rows)
        if 'PROJECT' in self.dataframes:
            self.dataframes['PROJECT'].set_index('proj_id', inplace=True)
        if 'CALENDAR' in self.dataframes:
            self.dataframes['CALENDAR'].set_index('clndr_id', inplace=True)
        if 'TASKPRED' in self.dataframes and 'task_pred_id' in self.dataframes['TASKPRED'].columns:
            self.dataframes['TASKPRED'].set_index('task_pred_id', inplace=True)
        if 'TASK' in self.dataframes:
            task_df = self.dataframes['TASK']
            if 'proj_id' in task_df.columns and 'task_code' in task_df.columns:
                self.dataframes['TASK'].index = task_df['proj_id'].astype(str) + "__" + task_df['task_code'].astype(str)
            for col in ['target_drtn_hr_cnt','remain_drtn_hr_cnt','total_float_hr_cnt','free_float_hr_cnt']:
                if col in task_df.columns:
                    self.dataframes['TASK'][col] = pd.to_numeric(self.dataframes['TASK'][col], errors='coerce').fillna(0.0)
        if 'TASKPRED' in self.dataframes and 'lag_hr_cnt' in self.dataframes['TASKPRED'].columns:
            self.dataframes['TASKPRED']['lag_hr_cnt'] = pd.to_numeric(self.dataframes['TASKPRED']['lag_hr_cnt'], errors='coerce').fillna(0.0)

    def _parse_activities(self):
        if 'TASK' not in self.dataframes:
            return
        for _, row in self.dataframes['TASK'].iterrows():
            a = Activity()
            a.task_id       = str(row.get('task_id',            '') or '')
            a.task_code     = str(row.get('task_code',          '') or '')
            a.task_name     = str(row.get('task_name',          '') or '')
            a.wbs_id        = str(row.get('wbs_id',             '') or '')
            a.calendar_id   = str(row.get('clndr_id',           '') or '')
            a.task_type     = str(row.get('task_type',          '') or '')
            a.status_code   = str(row.get('status_code',        '') or '')
            a.constraint    = str(row.get('cstr_type',          '') or '')
            a.constraint2   = str(row.get('cstr_type2',         '') or '')
            a.start         = str(row.get('early_start_date',   '') or '')
            a.finish        = str(row.get('early_end_date',     '') or '')
            a.act_start     = str(row.get('act_start_date',     '') or '')
            a.act_finish    = str(row.get('act_end_date',       '') or '')
            a.proj_id       = str(row.get('proj_id',            '') or '')
            a.duration      = float(row.get('target_drtn_hr_cnt', 0) or 0)
            a.remaining_dur = float(row.get('remain_drtn_hr_cnt',  0) or 0)
            a.total_float   = float(row.get('total_float_hr_cnt',  0) or 0)
            a.free_float    = float(row.get('free_float_hr_cnt',   0) or 0)
            a.successors    = []
            a.predecessors  = []
            self.activities[a.task_id] = a

    def _parse_relationships(self):
        if 'TASKPRED' not in self.dataframes:
            return
        for _, row in self.dataframes['TASKPRED'].iterrows():
            r = Relationship()
            r.pred_task_id = str(row.get('pred_task_id', '') or '')
            r.succ_task_id = str(row.get('task_id',      '') or '')
            r.pred_type    = str(row.get('pred_type',    'PR_FS') or 'PR_FS')
            r.lag          = float(row.get('lag_hr_cnt', 0) or 0)
            self.relationships.append(r)

    def _link_relationships(self):
        for r in self.relationships:
            if r.succ_task_id in self.activities:
                self.activities[r.succ_task_id].predecessors.append(r)
            if r.pred_task_id in self.activities:
                self.activities[r.pred_task_id].successors.append(r)
