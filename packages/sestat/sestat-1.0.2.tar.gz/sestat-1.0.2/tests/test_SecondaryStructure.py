import unittest

from src.sestat import Structure, Rail, Circle, SecondaryStructure


class TestSecondaryStructure(unittest.TestCase):
    def test_encode_rle(self):
        sequence1 = '.5(2)3'
        result1 = SecondaryStructure.encode_rle(sequence1)
        self.assertEqual(result1, '.....(()))')

        sequence2 = '.()3(2.'
        result2 = SecondaryStructure.encode_rle(sequence2)
        self.assertEqual(result2, '.()))((.')

    def test_load1(self):
        reference = ('ACT'
                     'GAC'
                     'TGA'
                     'CTG'
                     'A'
                     'C'
                     'TGAC')
        structure = '(((...)))...(+)....'
        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)
        rail1 = Rail()
        rail2 = Rail()
        circle1 = Circle()
        root = Circle()

        rail1.elements = ['A', 'C', 'T', circle1, 'T', 'G', 'A']
        circle1.elements = ['G', 'A', 'C']

        rail2.elements = ['A', '+', 'C']

        root.elements = [rail1, 'C', 'T', 'G', rail2, 'T', 'G', 'A', 'C']
        circle1.parent = rail1
        rail1.parent = root
        rail2.parent = root

        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root
        self.assertEqual(secondary_structure1, secondary_structure2)

        structure = '(3.3)3.3(+)1.4'
        secondary_structure1.load_from_rle(reference, structure)
        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load2(self):
        reference = 'GAAGTCC'
        structure = '((..).)'

        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)
        root = Circle()
        rail1 = Rail()
        rail2 = Rail()
        circle1 = Circle()
        circle2 = Circle()
        circle2.elements = ['A', 'G']
        rail2.elements = ['A', circle2, 'T']
        circle1.elements = [rail2, 'C']
        rail1.elements = ['G', circle1, 'C']
        root.elements = [rail1]

        rail1.parent = root
        circle1.parent = rail1
        rail2.parent = circle1
        circle2.parent = rail2

        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root
        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load3(self):
        reference = 'ACGTTCT'
        structure = '(.(..))'
        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)

        root = Circle()
        rail1 = Rail()
        rail2 = Rail()
        circle1 = Circle()
        circle2 = Circle()
        circle2.elements = ['T', 'T']
        rail2.elements = ['G', circle2, 'C']
        circle1.elements = ['C', rail2]
        rail1.elements = ['A', circle1, 'T']
        root.elements = [rail1]

        rail1.parent = root
        circle1.parent = rail1
        rail2.parent = circle1
        circle2.parent = rail2

        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root
        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load4(self):
        reference = 'AGCT'
        structure = '(.+.)'
        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)

        root = Circle()
        rail1 = Rail()
        circle1 = Circle()
        circle1.elements = ['G', '+', 'C']
        rail1.elements = ['A', circle1, 'T']
        root.elements = [rail1]

        rail1.parent = root
        circle1.parent = rail1

        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root
        self.assertEqual(secondary_structure1, secondary_structure2)

        reference = 'AGCT'
        structure = '(+..)'
        secondary_structure1.load_from_dot_parens(reference, structure)
        circle1.elements = ['+', 'G', 'C']
        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load5(self):
        reference = 'AGCTTGAT'
        structure = '(.(..)+.)'

        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)

        root = Circle()
        rail1 = Rail()
        circle1 = Circle()
        rail2 = Rail()
        circle2 = Circle()
        circle2.elements = ['T', 'T']
        rail2.elements = ['C', circle2, 'G']
        circle1.elements = ['G', rail2, '+', 'A']
        rail1.elements = ['A', circle1, 'T']
        root.elements = [rail1]

        circle2.parent = rail2
        rail2.parent = circle1
        circle1.parent = rail1
        rail1.parent = root

        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root

        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load6(self):
        reference = 'AAAAGGTTCCTT'
        structure = '((+((..))..))'

        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)

        root = Circle()
        rail1 = Rail()
        circle1 = Circle()
        rail2 = Rail()
        circle2 = Circle()
        circle2.elements = ['G', 'G']
        rail2.elements = ['A', 'A', circle2, 'T', 'T']
        circle1.elements = ['+', rail2, 'C', 'C']
        rail1.elements = ['A', 'A', circle1, 'T', 'T']
        root.elements = [rail1]
        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root

        rail1.parent = root
        circle1.parent = rail1
        rail2.parent = circle1
        circle2.parent = rail2

        self.assertEqual(secondary_structure1, secondary_structure2)

        reference = 'AAAAGGTTCCTT'
        structure = '((((..))+..))'

        secondary_structure1.load_from_dot_parens(reference, structure)
        circle1.elements = [rail2, '+', 'C', 'C']
        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load7(self):
        reference = 'ATGCCATAGCCAATTGG'
        structure = '((.((..))((..))))'
        secondary_structure1 = SecondaryStructure()
        secondary_structure1.load_from_dot_parens(reference, structure)

        root = Circle()
        rail1 = Rail()
        rail2 = Rail()
        rail3 = Rail()
        circle1 = Circle()
        circle2 = Circle()
        circle3 = Circle()
        circle2.elements = ['A', 'T']
        rail2.elements = ['C', 'C', circle2, 'A', 'G']
        circle3.elements = ['A', 'A']
        rail3.elements = ['C', 'C', circle3, 'T', 'T']
        circle1.elements = ['G', rail2, rail3]
        rail1.elements = ['A', 'T', circle1, 'G', 'G']
        root.elements = [rail1]

        rail1.parent = root
        circle1.parent = rail1
        rail2.parent = circle1
        rail3.parent = circle1
        circle3.parent = rail3
        circle2.parent = rail2

        secondary_structure2 = SecondaryStructure()
        secondary_structure2.root = root

        self.assertEqual(secondary_structure1, secondary_structure2)

    def test_load_exceptions(self):
        secondary_structure = SecondaryStructure()

        reference = 'AGT'
        structure = '....'
        self.assertRaises(ValueError, secondary_structure.load_from_dot_parens, reference,
                          structure)

        reference = 'AGTC'
        structure = '.../'
        self.assertRaises(ValueError, secondary_structure.load_from_dot_parens, reference,
                          structure)

        reference = 'AG'
        structure = '....'
        secondary_structure = SecondaryStructure()
        self.assertRaises(ValueError, secondary_structure.load_from_dot_parens, reference,
                          structure)

        with self.assertLogs('SecondaryStructure', 'WARNING') as cm:
            reference = 'AAAAAAAAA'
            structure = '.....'
            secondary_structure.load_from_dot_parens(reference, structure)
            self.assertEqual(['WARNING:SecondaryStructure:'
                              'Reference is longer, rest of bases will not be used'], cm.output)

    def test_eq(self):
        self.assertEqual(SecondaryStructure(), SecondaryStructure())
        self.assertNotEqual(SecondaryStructure(), 1)

    def test_empty(self):
        secondary_structure = SecondaryStructure()
        self.assertTrue(secondary_structure.is_empty())

        secondary_structure.load_from_dot_parens('AGT', '...')
        self.assertFalse(secondary_structure.is_empty())


class TestStructure(unittest.TestCase):
    def test_eq(self):
        self.assertEqual(Structure(), Structure())
        self.assertNotEqual(Structure(), 1)

        structure1 = Structure()
        structure1.elements = [1, 2, 3]

        structure2 = Structure()
        structure2.elements = [1, 2, 3]
        self.assertEqual(structure1, structure2)

        structure1.elements = [1, 2, 5]
        structure2.elements = [1, 2, 3]
        self.assertNotEqual(structure1, structure2)

        structure1.elements = [1, 2]
        structure2.elements = [1, 2, 3]
        self.assertNotEqual(structure1, structure2)

        circle1 = Circle()
        circle1.elements = [1, 2, 3]
        circle2 = Circle()
        circle2.elements = [1, 2, 3]

        structure1.elements = [1, 2, circle1]
        structure2.elements = [1, 2, circle2]
        self.assertEqual(structure1, structure2)

        circle1.elements = [1, 2, 5]
        circle2.elements = [1, 2, 3]
        self.assertNotEqual(structure1, structure2)

        circle1.elements = [1, 2]
        circle2.elements = [1, 2, 3]
        self.assertNotEqual(structure1, structure2)

        structure1.elements = [1, 2, 3]
        structure2.elements = [1, 2, 3]
        structure1.parent = Structure()
        self.assertNotEqual(structure1, structure2)

    def test_class_link(self):
        structure1 = Structure()
        structure1.elements = [1, 2, 3]
        structure2 = structure1
        self.assertTrue(structure1 == structure2)

        structure1.elements = [1, 2]
        self.assertTrue(structure1 == structure2)
        self.assertEqual(structure2.elements, [1, 2])

    def test_assign(self):
        structure1 = Structure()
        structure1.elements = [1, 2, 3]
        self.assertEqual(structure1.elements, [1, 2, 3])

        structure1.elements.append(5)
        self.assertEqual(structure1.elements, [1, 2, 3, 5])
