def run(path) :     
    # import modules here 
    import pandas as pd 

    # logic 
    sheets = pd.read_excel(path, sheet_name=None)
    attendance_df = sheets[list(sheets.keys())[0]]
    student_df = sheets[list(sheets.keys())[1]]

    
    attendance_df = attendance_df[attendance_df['status'] == 'A']
    attendance_df['attendance_date'] = pd.to_datetime(attendance_df['attendance_date'])
    attendance_df = attendance_df.sort_values(by=['student_id', 'attendance_date'])

    def get_latest_streak(group):
        group = group.sort_values(by='attendance_date').reset_index(drop=True)
        streak = []
        latest = []

        for i in range(len(group)):
            if not streak:
                streak = [group.loc[i, 'attendance_date']]
            else:
                if (group.loc[i, 'attendance_date'] - streak[-1]).days == 1:
                    streak.append(group.loc[i, 'attendance_date'])
                else:
                    if len(streak) >= 3:
                        latest = streak
                    streak = [group.loc[i, 'attendance_date']]
        if len(streak) >= 3:
            latest = streak

        if latest:
            return pd.DataFrame([{
                'student_id': group.loc[0, 'student_id'],
                'start_date': latest[0].date(),
                'end_date': latest[-1].date(),
                'total_absent_days': (latest[-1] - latest[0]).days + 1 
            }])
        else:
            return pd.DataFrame([])

    streaks = attendance_df.groupby('student_id').apply(get_latest_streak).reset_index(drop=True)
    df = pd.merge(streaks, student_df, on='student_id', how='left')


    def is_valid(email):
        if not isinstance(email, str):
            return False
        if '@' not in email:
            return False
        parts = email.split('@')
        if len(parts) != 2:
            return False
        local, domain = parts
        if domain != 'example.com':
            return False
        if not local:
            return False
        if local[0].isdigit():
            return False
        for ch in local:
            if not (ch.isalnum() or ch == '_'):
                return False
        return True

    df['email'] = df['parent_email'].apply(lambda x: x if is_valid(x) else "")

    def create_msg(row):
        if row['email']:
            return f"Dear Parent, your child {row['student_name']} was absent from {row['start_date']} to {row['end_date']} for {row['total_absent_days']} days. Please ensure their attendance improves."
        return ""

    df['msg'] = df.apply(create_msg, axis=1)

    return df
