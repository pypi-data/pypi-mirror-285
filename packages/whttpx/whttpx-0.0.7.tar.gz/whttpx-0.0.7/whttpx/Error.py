class Error_Auth(Exception):
  '''Credenciales de acceso'''
  def __init__(self, mensaje):
    self.mensaje = mensaje
    self.code=401

  def __str__(self):
        return self.mensaje