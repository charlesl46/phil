class User:
    def __init__(self,id,password,name) -> None:
        self.id = id
        self.password = password
        self.name = name
        pass

    def __str__(self) -> str:
        return f"Utilisateur {self.id} : {self.name}"

