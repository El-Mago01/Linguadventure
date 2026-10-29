from flask import render_template
class StudentStorageError(Exception):
    pass

class AdventureStorageError(Exception):
    pass


# ------------------------------------------------------------------------------------------
# Error handling
# ------------------------------------------------------------------------------------------
def register_error_handlers(app):

    @app.errorhandler(404)
    def wrong_user_input(e):
        """
        error handler for wrong user input - 404
        :param e:
        :return:
        """
        return render_template("error.html", code=404, message=e.description), 404


    @app.errorhandler(500)
    def internal_error(e):
        """
        Abort when an internal error occurred during execution - 500

        :param e:
        :return:
        """
        return render_template("error.html", code=500, message=e.description), 500


    @app.errorhandler(400)
    def bad_request(e):
        """
        Abort when a bad request error occurred - 400
        :param e:
        :return:
        """
        return render_template("error.html", code=400, message=e.description), 400