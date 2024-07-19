from wda import Element


def get_element_tree(element: Element, tree=None):
    if tree is None:
        tree = []

    tag_name = element.c.get('label', 'Unknow')
