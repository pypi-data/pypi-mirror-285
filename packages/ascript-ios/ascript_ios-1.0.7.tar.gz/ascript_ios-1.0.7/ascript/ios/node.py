from ascript.ios.wda import Selector as wda_selector, Element, Session

from ascript.ios import system


class Selector:
    MODE_EQUAL = 0
    MODE_CONTAINS = 1
    MODE_MATCHES = 2

    MODE_CLICK_ACCESS = 0
    MODE_CLICK_XY = 1

    MODE_SCROLL_VISIBLE = "visible"
    MODE_SCROLL_LEFT = "left"
    MODE_SCROLL_RIGHT = "right"
    MODE_SCROLL_UP = "up"
    MODE_SCROLL_DOWN = "down"

    def __init__(self):
        self.selector = {}
        self.click_action = None
        self.scroll_action = None
        self.set_text_action = None
        self.clear_text_action = None

    def find_with_dict(self, client, kv: dict, max_nums: int = 99999):
        self.selector = {}
        for k, v in kv.items():
            # self.selector[k] = v
            print(k, v)
            method = getattr(self, k, None)
            if method is not None and callable(method):
                if isinstance(v, list):
                    method(*v)
                else:
                    method(v)

        # print(max_nums)

        if max_nums > 1:
            return self.find_all(client)[:max_nums]
        else:
            return [self.find(client)]

    def find(self, client=system.client):
        elements = self.find_work(client=client)
        if elements and len(elements) > 0:
            self.append_action([elements[0]])
            return elements[0]

    def find_all(self, client=system.client):
        elements = self.find_work(client)
        self.append_action(elements)
        return elements

    def find_work(self, client=system.client):
        return wda_selector(client, **self.selector).find_elements()

    def append_action(self, elements):
        for element in elements:
            if self.click_action:
                element.click()

            if self.scroll_action:
                # print(self.scroll_action)
                element.scroll(self.scroll_action["mode"], self.scroll_action["distance"])

            if self.clear_text_action:
                element.clear_text()

            if self.set_text_action is not None:
                if self.set_text_action == "":
                    element.clear_text()
                else:
                    element.set_text(self.set_text_action)

    def value(self, value, mode=MODE_EQUAL):
        if mode == self.MODE_EQUAL:
            self.selector["value"] = value
        elif mode == self.MODE_CONTAINS:
            self.selector["valueContains"] = value
        elif mode == self.MODE_MATCHES:
            self.selector["valueMatches"] = value
        return self

    def name(self, value: str, mode=MODE_EQUAL):
        if mode == self.MODE_EQUAL:
            self.selector["name"] = value
        elif mode == self.MODE_CONTAINS:
            self.selector["nameContains"] = value
        elif mode == self.MODE_MATCHES:
            self.selector["nameMatches"] = value
        return self

    def label(self, value: str, mode=MODE_EQUAL):
        if mode == self.MODE_EQUAL:
            self.selector["label"] = value
        elif mode == self.MODE_CONTAINS:
            self.selector["labelContains"] = value
        elif mode == self.MODE_MATCHES:
            self.selector["labelMatches"] = value
        return self

    def type(self, value):
        self.selector["type"] = value
        return self

    def visible(self, value: bool):
        self.selector["visible"] = value
        return self

    def enabled(self, value: bool):
        self.selector["enabled"] = value
        return self

    def index(self, value: int):
        self.selector["index"] = value
        return self

    def xpath(self, value: str):
        self.selector["xpath"] = value
        return self

    def predicate(self, value: str):
        self.selector["predicate"] = value
        return self

    def click(self, mode=MODE_CLICK_XY):
        self.click_action = mode
        return self

    def scroll(self, mode=MODE_SCROLL_VISIBLE, distance: float = 1.0):
        self.scroll_action = {"mode": mode, "distance": distance}
        return self

    def input(self, value):
        self.set_text_action = value
        return self

    def clear_text(self, *args):
        self.clear_text_action = 1
        return self


class AsElement(Element):
    # http://127.0.0.1:58817/session/A93BC308-3B79-42D0-B13C-240DA9D3D953/element/BF000000-0000-0000-2000-000000000000/attribute/rect
    def __init__(self, session: Session, id: str):
        super().__init__(session, id)

    @property
    def index(self):
        return self._prop('attribute/index')

    def screenshot(self):
        return self._prop("screenshot")

    @property
    def attr(self):
        return self._prop('attribute')
