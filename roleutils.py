def has_role(member, role):
    for y in member.roles:
        yname = str(y.name).lower()
        role = str(role.lower())
        if yname == role:
            return True
    return False
    


def is_officer(member):
    return has_role(member, "officer") or has_role(member, "senior officer") or has_role(member, "General Of The Army")
