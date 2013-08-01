class Law(object):
    def __init__(self, id_, title, text):
        self.id_ = id_
        self.title = title
        self.text = text

    def append_text(self, text):
        self.text += text


class OregonRevisedStatute(Law):
    DIVISION_NAME = 'Chapter'
    PREFIX = 'ORS'

    def __str__(self):
        return 'ORS {id}. {title}'.format(
            id=self.id_, title=self.title)

    @property
    def filename(self):
        return self.id_

    @property
    def full_law(self):
        return '{id}. {title}\n{text}'.format(
            id=self.id_,
            title=self.title,
            text=self.text)

