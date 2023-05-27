# Create your views here.
def list_to_string(list_values):
    return ', '.join(list_values)

def sort_key(lst, unique_id):
    if unique_id in lst:
        return lst.index(unique_id)
    else:
        return len(lst)
    
def check_item_org(db, cus_id, org_id, table, id_field):
        check_user_query = f"""select * from {table}
                    where {id_field}='{cus_id}' and inf_org_id = '{org_id}' and inf_is_deleted = FALSE"""
        user_df = db.select_rows_dict(check_user_query)

        if (len(user_df.values)):
            return True
        else:
            return False