def sql_check_if_member_exists(member_id): 
    return f"SELECT * FROM members WHERE member_id = {member_id} LIMIT 1"
    
def sql_insert_member(member_id):
    return f"INSERT INTO members (member_id) VALUES ('{member_id}')"

def sql_delete_member(member_id): 
    return f"DELETE FROM members WHERE member_id = {member_id}"
