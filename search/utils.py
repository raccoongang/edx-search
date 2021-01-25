""" Utility classes to support others """
import importlib
import collections
import logging


log = logging.getLogger(__name__)  # pylint: disable=invalid-name

# The order of courses is important
COURSES_ORDER = [
    "course-v1:Lakeside+TE101+2019",  # The Essentials of Trauma - The Opioid Crisis
    "course-v1:NeuroLogic+NL101+2020Q2",  # The Trauma-Informed Classroom
    "course-v1:Neurologic+NCS101+2021_T2",  # NeuroLogic Coaching Sessions
    "course-v1:Neurologic+NL105+2021_T1",  # Resilience: Increasing Students' Tolerance for Stress
    "course-v1:LakesideGlobalInstitute+2000+2020_T1",  # Enhancing Trauma Awareness
    "course-v1:Lakeside+PRE1101+2020",  # PRESENCE - Introductory Track
    "course-v1:Lakeside+PRE1101+2020_T2",  # PRESENCE-Leadership Track
    "course-v1:Lakeside+PRE1103+2029_T2",  # PRESENCE - Clinical Track
]


def _load_class(class_path, default):
    """ Loads the class from the class_path string """
    if class_path is None:
        return default

    component = class_path.rsplit('.', 1)
    result_processor = getattr(
        importlib.import_module(component[0]),
        component[1],
        default
    ) if len(component) > 1 else default

    return result_processor


def _is_iterable(item):
    """ Checks if an item is iterable (list, tuple, generator), but not string """
    return isinstance(item, collections.Iterable) and not isinstance(item, basestring)


class ValueRange(object):

    """ Object to represent a range of values """

    def __init__(self, lower=None, upper=None):
        self._lower = lower
        self._upper = upper

    @property
    def upper(self):
        """ return class member _upper as a proerty value """
        return self._upper

    @property
    def lower(self):
        """ return class member _lower as a proerty value """
        return self._lower

    @property
    def upper_string(self):
        """ return string representation of _upper as a proerty value """
        return str(self._upper)

    @property
    def lower_string(self):
        """ return string representation of _upper as a proerty value """
        return str(self._lower)


class DateRange(ValueRange):

    """ Implemetation of ValueRange for Date """
    @property
    def upper_string(self):
        """ use isoformat for _upper date's string format """
        return self._upper.isoformat()

    @property
    def lower_string(self):
        """ use isoformat for _lower date's string format """
        return self._lower.isoformat()


def sort_courses_by_hardcoded_ids_order(data):
    """
    Sort a batch of courses as per the course ids hardcoded order.

    "programs" value will be updated, in particular, a respective batch of courses,
    where the courses of interest appear.

    Sequence of hardcoded courses will go first in its courses group.

    NOTE: consider separating out results parsing from courses batch reordering.

    Arguments:
        data (dict): nested search results. Example:
        ```
        {
            'programs_total': 15,
            'programs': [
                {
                    'subtitle': u'',
                    'title': u'Lakeside Demo',
                    'courses': [
                        {
                            u'_type': u'course_info',
                            'score': 1.0,
                            u'_index': u'courseware_index',
                            u'_score': 1.0,
                            u'_id': u'course-v1:honor01+101+2019',
                            'data': {
                                u'category': [u'Category 1 1 1 1 1'],
                                u'product': False,
                                u'end': u'2022-01-01T00:00:00+00:00',
                                u'modes': [u'honor'],
                                # ...
                            }
                            # ...
                        }
                    ],
                },
            ],
            # ...  'facets', 'took', 'results', 'total', 'max_score' ...
        }
        ```

    Returns:
        data with re-ordered courses in a certain group (dict)
    """
    programs = data.get("programs")
    unsorted_first_courses_data = {}

    first_courses = []
    other_courses = []
    # To remember a program containing courses of interest
    program_index = None

    # Separate out all the courses, excluding the ones configured in COURSES_ORDER
    # Also, remember the program index containing the courses from COURSES_ORDER
    for i, program in enumerate(programs):
        p_courses = program.get("courses")
        for p_course in p_courses:
            course_key = p_course.get("_id")
            if course_key in COURSES_ORDER:
                program_index = i
                unsorted_first_courses_data[course_key] = p_course
            elif program_index is not None:
                other_courses.append(p_course)
        # Course ids are unique, so courses with same ids can't appear in other programs
        if program_index is not None:
            break

    # Populate the courses of interest i.e. the ones we reorder
    for config_key in COURSES_ORDER:
        course = unsorted_first_courses_data.get(config_key)
        if course:
            first_courses.append(course)

    sorted_data = dict(data)
    if first_courses and program_index is not None:
        sorted_data["programs"][program_index]["courses"] = first_courses + other_courses

    return sorted_data
