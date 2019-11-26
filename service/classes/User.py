class User:

    def __init__(self, user_id, firstname, lastname, email, is_active, is_admin, dateofbirth, token, authenticated):
      self.id = user_id
      self.firstname = firstname
      self.lastname = lastname
      self.email = email
      self.dateofbirth = dateofbirth
      self.is_active = is_active
      self.is_admin = is_admin
      self.token = token
      self._authenticated = authenticated

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self._authenticated
