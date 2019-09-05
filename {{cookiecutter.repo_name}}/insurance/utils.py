import datetime
from collections import namedtuple


def to_namedtuple(obj):
    if hasattr(obj, 'keys'):
        return namedtuple('NamedTuple', obj.keys())(**obj)
    elif hasattr(obj, '__iter__'):
        return namedtuple('NamedTuple', obj)(*obj)
    else:
        raise AssertionError('Only dict type or iter type argument is supported')


def get_namedtuple_choices(choices_tuple, name='NamedChoices'):
    """Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = get_namedtuple_choices('COLORS', (
                (0, 'BLACK', 'Black'),
                (1, 'WHITE', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)

        >>> MyModel.COLORS.BLACK
        0
        >>> MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'FR', 'Freshman'),
                ('SR', 'SR', 'Senior'),
            ))
            # Or
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'Freshman'),
                ('SR', 'Senior'),
            ))
            # Or
            GRADES = get_namedtuple_choices({
                'FR': 'Freshman',
                'SR': 'Senior',
            })
            grade = models.CharField(max_length=2, choices=GRADES)

        >>> OtherModel.GRADES.FR
        'FR'
        >>> OtherModel.GRADES.get_choices()
        [('FR', 'Freshman'), ('SR', 'Senior')]


    """
    if hasattr(choices_tuple, 'items'):
        choices_tuple = choices_tuple.items()

    class Choices(namedtuple(name, [choice[-2] for choice in choices_tuple])):  # list comprehension gets the name
        __slots__ = ()
        _choices = tuple([choice[-1] for choice in choices_tuple])  # list comprehension gets the description

        def get_choices(self):
            return zip(tuple(self), self._choices)

    return Choices._make([choice[0] for choice in choices_tuple])  # list comprehension gets the value


def get_years_from(date, years):
    """
    Gives you <years> from <date>
    date + years
    """
    return date.replace(year=date.year + years) - datetime.timedelta(days=1)
