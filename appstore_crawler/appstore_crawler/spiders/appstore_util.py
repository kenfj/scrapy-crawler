
def snake_case(words):
    # adjust to url (Food & Drink -> food-drink)
    return words.replace(' & ', '-').replace(' ', '-').lower()
