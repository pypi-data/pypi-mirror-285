~~~~~~~~~~~~~~~~~~~~~
FletNavigator V2.8.5
~~~~~~~~~~~~~~~~~~~~~

.. image :: https://github.com/xzripper/flet_navigator/raw/main/example2.gif
   :width: 500

FletNavigator & `FletReStyle <https://github.com/xzripper/flet_restyle>`_

Simple and fast navigator (router) for Flet (Python) that provides everything for comfortable and easy multi-page applications creation.

Click `here <https://github.com/xzripper/flet_navigator/blob/main/flet-navigator-docs.md>`_ for documentation.

Using Example:

.. code :: python

   from flet import app, Text

   from flet_navigator import PageData, render, anon, route


   @route('/')
   def main_page(pg: PageData) -> None:
      pg.add(Text('Main Page!')) # or `pg.page.add`.

   @route('second_page')
   def second_page(pg: PageData) -> None:
      ... # Second page content.

   app(anon(render, virtual=True))

.. image :: https://raw.githubusercontent.com/xzripper/flet_navigator/main/example.gif
   :width: 400

(Deprecated Example GIF).

`Documentation & GitHub. <https://github.com/xzripper/flet_navigator/blob/main/flet-navigator-docs.md>`_

-----------------------------------------------

   FletNavigator V2.8.5
