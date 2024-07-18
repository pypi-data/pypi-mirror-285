class Auth:
    def login(self, user, pwd):
        print("User logged")

        token = "123123zcsfsfsdf1"
        return token

    def is_logged(self, token):
        return True


if __name__ == "__main__":
    auth = Auth()
    auth.login("Diego", "123")
