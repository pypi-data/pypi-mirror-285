########################################################################
#                            PHASED OUT                                #
########################################################################


# FROM:  BA_api_routing.py


@BA_api_flask_blueprint.route('/download_test')
def download_test():
    # EXAMPLE invocation: http://localhost:5000/api/download
    #return "test"
    response = make_response("Dynamic data to download")
    response.headers['Content-Type'] = 'application/save'
    response.headers['Content-Disposition'] = 'attachment; filename=\"exported_json_data.txt\"'
    return response





# FROM: neo_schema.py

    @classmethod
    def add_new_category(cls, name: str, remarks=None, parent_category_id=1) -> int:
        """ superseded by add_subcategory() in BA_api_request_handler

        :param name:
        :param remarks:
        :param parent_category_id:  1 is the ROOT category
        :return:                    In case of error, a string with an error message; otherwise, an empty string
        """
        data_dict = {"name": name}
        if remarks:
            data_dict["remarks"] = remarks

        return cls.add_data_point_OLD("Categories", data_dict, labels="BA",
                                      connected_to_id=parent_category_id, connected_to_labels="BA", rel_name="BA_subcategory_of", rel_dir="OUT")


# FROM: test_neoschema.py

def test_add_new_category():
    status = NeoSchema.add_new_category("Language", parent_category_id=1)
    assert status == ""




# FROM: categories.py

    @classmethod
    def lookup_Nth_item_pos_NOT_IN_USE(cls, category_id :str, n: int) -> Union[int, None]:  # TODO: if not needed, zap
        """
        Look up and return the "position" (a database-stored integer used to establish the relative page positions of Content Items)
        of the n-th Content Item (counting starts with 1), in the context of the positioning for the given Category.

        If not found, return None

        EXAMPLE: if Category ID 60 contains
                            uri	pos
                                555	0
                                509	15
                                508	40
                  then  lookup_Nth_item_pos(60, 1) = 0
                        lookup_Nth_item_pos(60, 2) = 15
                        lookup_Nth_item_pos(60, 3) = 40
                  and any other value of the 2nd argument will yield None

        :param category_id: A string with the Category ID
        :param n:           An integer 1 or larger, meaning the n-th Content Item attached to the above Category
                                (as sorted by the "pos" attribute)
        :return:            The integer with the value of the "pos" attribute of the Content Item, if located,
                                or None if not found
        """
        assert type(category_id) == str, "ERROR: argument 'category_id' is not a string"
        assert type(n) == int, "ERROR: argument 'n' is not an integer"

        if n < 1:
            return None

        number_to_skip = n - 1  # So, for example, if we want the 1st item, we skip zero entries

        q = f'''
            MATCH (c:BA {{schema_code: "cat", uri: $category_id}}) <- [r:BA_in_category] - (n)
            RETURN  r.pos AS pos
            ORDER by pos
            SKIP {number_to_skip}
            LIMIT 1
        '''

        return cls.db.query(q, {"category_id": category_id}, single_cell="pos")     # This will be None if nothing found
