import logging

from .Structure import Structure, Circle, Rail, RailState


class SecondaryStructure:
    def __init__(self):
        self.root: Circle | None = None

    def is_empty(self):
        return self.root is None

    def load_from_dot_parens(self, reference: str, structure: str) -> None:
        """Loads structure and makes available for processing"""

        length_of_strands = len(structure) - structure.count('+')
        if length_of_strands > len(reference):
            raise ValueError("Reference is too short")
        elif length_of_strands < len(reference):
            (logging.getLogger('SecondaryStructure').
             warning("Reference is longer, rest of bases will not be used"))

        for symbol in structure:
            if symbol not in '.()+':
                raise ValueError(f'Unsupported symbol in structure "{symbol}"')

        current = self.root = Circle()
        reference_counter = 0

        for symbol in structure:
            if isinstance(current, Circle):
                if symbol == '.':
                    current.elements.append(reference[reference_counter])
                elif symbol == '+':
                    current.elements.append('+')
                elif symbol == '(':
                    rail = Rail()
                    rail.elements.append(reference[reference_counter])
                    rail.can_contain = 1
                    current.elements.append(rail)
                    rail.parent = current
                    current = rail
                elif symbol == ')':
                    current = current.parent
                    current.state = RailState.FINISHING
                    current.elements.append(reference[reference_counter])
                    current.can_contain -= 1
            elif isinstance(current, Rail):
                if current.state == RailState.ADDING:
                    if symbol == '(':
                        current.elements.append(reference[reference_counter])
                        current.can_contain += 1
                    elif symbol == ')':
                        current.elements.append(reference[reference_counter])
                        current.can_contain -= 1
                        current.state = RailState.FINISHING
                    elif symbol == '+':
                        current.elements.append('+')
                    elif symbol == '.':
                        circle = Circle()
                        if current.elements[-1] == '+':
                            current.elements.pop()
                            circle.elements.append('+')
                        circle.elements.append(reference[reference_counter])
                        current.elements.append(circle)
                        circle.parent = current
                        current = circle
                elif current.state == RailState.FINISHING:
                    if symbol == '+':
                        if not current.can_contain:
                            current = current.parent
                        current.elements.append('+')
                    elif symbol == '.':
                        if not current.can_contain:
                            current = current.parent
                            current.elements.append(reference[reference_counter])
                        else:
                            rail1 = Rail()
                            rail2 = Rail()
                            circle = Circle()

                            i = 0
                            while len(rail1.elements) - rail1.elements.count(
                                    '+') < current.can_contain:
                                rail1.elements.append(current.elements[i])
                                i += 1
                            rail1.can_contain = current.can_contain

                            if current.elements[i] == '+':
                                i += 1
                                circle.elements.append('+')

                            rail2.elements = current.elements[i:]

                            rail1.parent = current.parent
                            rail1.elements.append(circle)

                            rail2.parent = circle

                            circle.parent = rail1
                            circle.elements.append(rail2)
                            if rail2.elements[-1] == '+':
                                rail2.elements.pop()
                                circle.elements.append('+')
                            circle.elements.append(reference[reference_counter])

                            current.parent.elements.pop()
                            current.parent.elements.append(rail1)
                            current = circle
                    elif symbol == ')':
                        if current.can_contain:
                            current.elements.append(reference[reference_counter])
                            current.can_contain -= 1
                        else:
                            current = current.parent.parent
                            current.state = RailState.FINISHING
                            current.elements.append(reference[reference_counter])
                            current.can_contain -= 1
                    elif symbol == '(':
                        rail = Rail()
                        rail.elements.append(reference[reference_counter])
                        rail.can_contain = 1

                        current.parent.elements.append(rail)
                        rail.parent = current.parent

                        current = rail

            if symbol != '+':
                reference_counter += 1

    def load_from_rle(self, reference: str, structure: str) -> None:
        """Encodes RLE dot parenthesis structure and loads"""

        encoded_structure: str = self.encode_rle(structure)
        self.load_from_dot_parens(reference, encoded_structure)

    @staticmethod
    def encode_rle(sequence: str) -> str:
        """Encodes RLE sequence"""
        encoded_rle: str = ''

        symbol: str = ''
        number: str = ''

        # additional symbol to add last result in encoded structure
        sequence += '/'
        for char in sequence:
            if char.isdigit():
                number += char
            else:
                if number:
                    encoded_rle += symbol * int(number)
                else:
                    encoded_rle += symbol
                symbol = char
                number = ''

        return encoded_rle

    def __eq__(self, other):
        if type(self) is type(other):
            return self.root == other.root
        return False

    def __ne__(self, other):
        return not self.__eq__(other)
