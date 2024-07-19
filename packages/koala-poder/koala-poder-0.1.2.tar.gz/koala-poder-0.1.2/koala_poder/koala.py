class Koala:
    def __init__(self, name, poder, action):
        self.name = name
        self.poder = poder
        self.action = action

    def hello_koala(self):
        print(f"Hello everyone! My name is {self.name}, and I am a koala llena de poder!")

    def use_koala_poder(self):
        print(f"{self.name} attacked the forces of evil with their poder of {self.poder}")

    def koala_action(self):
        print(f"{self.name} decided to {self.action}! How beautiful!")

    def koala_add(self, num1, num2):
        result = num1 + num2
        return f"{self.name} learned to add numbers. Today {self.name} added {num1} and {num2} to get {result}!"
