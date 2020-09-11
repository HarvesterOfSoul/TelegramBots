class CreateUser:
    def __init__(self, api_id, api_hash, session_name, battle_group):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_name = session_name
        self.battle_group = battle_group


mike = CreateUser(api_id=243333, api_hash='0449781cff2618594375fb843f401f4a', session_name='TheRealNoob', battle_group='https://t.me/joinchat/Fa7eDBCqd')
danny = CreateUser(api_id=239475, api_hash='d0b82d685b49df2b17c8a810967d1aea', session_name='Danny', battle_group='https://t.me/joinchat/Fa7eDBCqd')
player3 = CreateUser(api_id=414717, api_hash='99f0a60f8f4714a9b1f83761f0cc075b', session_name='Caroline', battle_group='https://t.me/joinchat/JkHQ9VMP')
player4 = CreateUser(api_id=485341, api_hash='c610c6ae29820cdf2d7c40a1d899f53b', session_name='Matt', battle_group='https://t.me/joinchat/JkHQ9VMP')


type_dict = {
    "Normal": {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 0.5, "Ghost": 0, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Fire": {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Electric": 1, "Grass": 2, "Ice": 2, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 2, "Rock": 0.5, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 2, "Fairy": 1},
    "Water": {"Normal": 1, "Fire": 2, "Water": 0.5, "Electric": 1, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 2, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 2, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 1, "Fairy": 1},
    "Electric": {"Normal": 1, "Fire": 1, "Water": 2, "Electric": 0.5, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 0, "Flying": 2, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 1, "Fairy": 1},
    "Grass": {"Normal": 1, "Fire": 0.5, "Water": 2, "Electric": 1, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Psychic": 1, "Bug": 0.5, "Rock": 2, "Ghost": 1, "Dragon": 0.5, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Ice": {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Electric": 1, "Grass": 2, "Ice": 0.5, "Fighting": 1, "Poison": 1, "Ground": 2, "Flying": 2, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Fighting": {"Normal": 2, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 2, "Fighting": 1, "Poison": 0.5, "Ground": 1, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dragon": 1, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison": {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 2, "Ice": 1, "Fighting": 1, "Poison": 0.5, "Ground": 0.5, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 0.5, "Ghost": 0.5, "Dragon": 1, "Dark": 1, "Steel": 0, "Fairy": 2},
    "Ground": {"Normal": 1, "Fire": 2, "Water": 1, "Electric": 2, "Grass": 0.5, "Ice": 1, "Fighting": 1, "Poison": 2, "Ground": 1, "Flying": 0, "Psychic": 1, "Bug": 0.5, "Rock": 2, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 2, "Fairy": 1},
    "Flying": {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 0.5, "Grass": 2, "Ice": 1, "Fighting": 2, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 2, "Rock": 0.5, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Psychic": {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 2, "Poison": 2, "Ground": 1, "Flying": 1, "Psychic": 0.5, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 0, "Steel": 0.5, "Fairy": 1},
    "Bug": {"Normal": 1, "Fire": 0.5, "Water": 1, "Electric": 1, "Grass": 2, "Ice": 1, "Fighting": 0.5, "Poison": 0.5, "Ground": 1, "Flying": 1, "Psychic": 0.5, "Bug": 2, "Rock": 1, "Ghost": 0.5, "Dragon": 1, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock": {"Normal": 1, "Fire": 2, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 2, "Fighting": 0.5, "Poison": 1, "Ground": 0.5, "Flying": 2, "Psychic": 1, "Bug": 2, "Rock": 1, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 1},
    "Ghost": {"Normal": 0, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 2, "Rock": 1, "Ghost": 2, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 1},
    "Dragon": {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 1, "Steel": 0.5, "Fairy": 0},
    "Dark": {"Normal": 1, "Fire": 1, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 0.5, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 2, "Bug": 1, "Rock": 1, "Ghost": 2, "Dragon": 1, "Dark": 0.5, "Steel": 1, "Fairy": 0.5},
    "Steel": {"Normal": 1, "Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Grass": 1, "Ice": 2, "Fighting": 1, "Poison": 1, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 2, "Ghost": 1, "Dragon": 1, "Dark": 1, "Steel": 0.5, "Fairy": 2},
    "Fairy": {"Normal": 1, "Fire": 0.5, "Water": 1, "Electric": 1, "Grass": 1, "Ice": 1, "Fighting": 2, "Poison": 0.5, "Ground": 1, "Flying": 1, "Psychic": 1, "Bug": 1, "Rock": 1, "Ghost": 1, "Dragon": 2, "Dark": 2, "Steel": 0.5, "Fairy": 1}
}
