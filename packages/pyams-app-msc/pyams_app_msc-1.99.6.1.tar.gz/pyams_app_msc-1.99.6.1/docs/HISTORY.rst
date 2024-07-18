Changelog
=========

1.99.6.1
--------
 - packaging issue

1.99.6
------
 - added paragraphs support to movie theaters
 - added workflow publication support to movie theaters
 - updated skin colors and styles
 - display warning message when removing session with bookings
 - updated header logo getter
 - pre-select audience on new booking request
 - added movie theater SEO adapter
 - updated calendar event target URL
 - added link to catalog entry data from session booking form
 - updated refresh callbacks after booking workflow status update

1.99.5.1
--------
 - added control in page header renderer

1.99.5
------
 - issue #33: allow recipient notification when session is changed for booking
 - issue #34: automatically update sesion capacity when moved to a new room with higher capacity
 - issue #35: update dashboard on booking update
 - added user profile views
 - updated portlets and renderers for menus, navigation and styles

1.99.4
------
 - issue #27: added theater setting to set first week day displayed in calendars
 - issue #30: updated actions used to update content illustrations from medias gallery
 - issue #31: added free accompanists count in booking data
 - issue #32: allow direct booking validation from creation form
 - updated event title getter
 - updated user profile edit form
 - added column priority getter for use in responsive tables

1.99.3
------
 - issue #21: added display of principal phone number
 - issue #22: updated shared content header viewlet to add button to go back to dashboard
 - issue #25: updated prompt of activity selection widget
 - issue #26: added support for vertical synchronization of calendars
 - issue #27: removed theater week view from calendar
 - issue #30: added action to set content illustration from medias gallery image
 - issue #31: updated accompagnists price handler in quotations

1.99.2.4
--------
 - removed code dependency on OAuth authentication module (bis!)

1.99.2.3
--------
 - removed code dependency on OAuth authentication module

1.99.2.2
--------
 - updated tests requirements

1.99.2.1
--------
 - issue #24: updated booking value getter in dashboards

1.99.2
------
 - updated menus order
 - added paragraphs factory settings support to movie theater
 - updated booking recipient label
 - added structure type attribute to user profile
 - disable autocomplete on user profile creation form
 - added structures types references table
 - renamed MSC skin
 - updated movie theater breadcrumbs
 - added marker interface to user dashboard views
 - updated translations
 - updated session seats
 - updated session label adapter
 - added button in booking add form to automatically redirect to validation form after creation
 - updated AJAX finder URL to only get activities declared inside movie theater
 - removed unused fields from address
 - added tooltips on calendar events
 - added permission and role to manage references tables
 - allow theater manager to assign role to other managers
 - include TMDB images as gallery paragraph instead of global gallery
 - removed gallery support on catalog entries
 - disabled paragraphs associations menu
 - updated illustrations adapters
 - updated activity types forms (fixes issue #6)
 - added condition on bookings button display
 - added missing picture to Git
 - updated theater planning menu position

1.99.1
------
 - added edit forms content getters
 - added custom catalog entry roles adapters
 - removed roles restrictions menu entries from theater navigation menu
 - removed source folder from movie theater activity types properties (issue #6)
 - changed reminder delay unit from hours to days (issue #4]
 - updated theater settings edit form (issue #4)

1.99.0.1
--------
 - fixed packaging issue

1.99.0
------
 - first preliminary release
