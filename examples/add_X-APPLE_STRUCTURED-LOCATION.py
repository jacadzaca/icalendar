
'''Issue #116/#117 - How to add 'X-APPLE-STRUCTURED-LOCATION'
https://github.com/collective/icalendar/issues/116
https://github.com/collective/icalendar/issues/117
'''


def main():
    event = icalendar.Event()
    event.add(
        'X-APPLE-STRUCTURED-LOCATION',
        'geo:-33.868900,151.207000',
        parameters = {
            'VALUE': 'URI',
            'X-ADDRESS': '367 George Street Sydney CBD NSW 2000',
            'X-APPLE-RADIUS': '72',
            'X-TITLE': '367 George Street'
        }
    )

if __name__ == '__main__':
    main()
