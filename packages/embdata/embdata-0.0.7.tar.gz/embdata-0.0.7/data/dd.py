#!/usr/bin/env python3

from mbodied_data.sample import Sample
from typing import List, Dict

class Person(Sample):
    name: str
    age: int
    hobbies: List[str]
    scores: Dict[str, float] = {}

def main():
    # Create a Person instance
    person = Person(name="Alice", age=30, hobbies=["reading", "hiking", "photography"], scores={"math": 95.5, "science": 88.0})

    print("1. Basic Sample usage:")
    print(person)

    print("\n2. Dump output:")
    print(person.dump())

    print("\n3. Dict output:")
    print(person.dict())

    print("\n4. Schema:")
    print(person.schema())

    print("\n5. Flatten to list:")
    print(person.flatten())

    print("\n6. Flatten to dict:")
    print(person.flatten(output_type="dict"))

    print("\n7. To numpy array:")
    print(person.to("np"))

    print("\n8. To JSON:")
    print(person.to("json"))

    print("\n9. Space representation:")
    print(person.space())

    print("\n10. Random sample from space:")
    random_person = person.random_sample()
    print(random_person)

    print("\n11. Pack multiple samples:")
    person2 = Person(name="Bob", age=25, hobbies=["gaming", "cooking"], scores={"math": 89.0, "science": 92.5})
    packed = Person.unpack_from([person, person2])
    print(packed)

    print("\n12. Unpack samples:")
    unpacked = packed.pack()
    for p in unpacked:
        print(p)

    print("\n13. Custom container conversion:")
    class CustomContainer:
        def __init__(self, data):
            self.data = data

    custom_output = person.to(CustomContainer)
    print(f"Type: {type(custom_output)}, Data: {custom_output.data}")

if __name__ == "__main__":
    main()
