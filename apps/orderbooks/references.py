class PlantProductionReference:
    def __init__(self, plant: dict):
        self.plant = plant

    def get_alternate_name_for_float_product(self, sub_family: str) -> str | None:
        """
        get alternate names by sub-family name
        - e.g. sub_family: "PLANILUX" --> alternate: ["PLC"]
        - needed to work with planners (background: column 'tint' uses values of datalake's 'sub_family' attribute)
        """
        try:
            sub_family = sub_family.upper()
            output = self.plant["PRODUCT_FAMILIES"]["FLOAT"][sub_family]["alternate_name"]
            if output:
                return output
        except KeyError:
            pass
        except AttributeError:
            pass
        return None

    def get_alternate_names_for_coating_product(self, sub_family: str) -> list:
        """
        get alternate names by sub-family name
        - e.g. sub_family: "PLANILUX" --> alternate: ["PLC"]
        - needed to work with planners (background: column 'tint' uses values of datalake's 'sub_family' attribute)
        """
        try:
            sub_family = sub_family.upper()
            output = self.plant["PRODUCT_FAMILIES"]["WÄRMESCHUTZGLAS"][sub_family]["coating"]
            if output:
                return output
        except KeyError:
            pass
        except AttributeError:
            pass
        return list()

    def get_standing_time_of_coating(self, sub_family: str) -> int:
        """
        get standing time / rest time of coating after producing
        """
        try:
            sub_family = sub_family.upper()
            standing_time = self.plant["PRODUCT_FAMILIES"]["WÄRMESCHUTZGLAS"][sub_family]["standing_time"]
            return int(standing_time)
        except KeyError:
            pass
        except AttributeError:
            pass
        except TypeError:
            pass
        except ValueError:
            pass
        return 0

    def get_product_families_heat_protected_glass(self) -> list:
        """
        Get the product family coatings
        """
        return list(self.plant["PRODUCT_FAMILIES"]["WÄRMESCHUTZGLAS"].keys())

    def get_product_families_flat_glass(self):
        return list(self.plant["PRODUCT_FAMILIES"]["FLOAT"].keys())

    def get_coatings_for_subfamily(self, subfamily: str) -> list[str]:
        """
        Get the coatings for the given subfamily
        """
        return self.plant["PRODUCT_FAMILIES"]["WÄRMESCHUTZGLAS"][subfamily]["coating"]

    def get_flat_coatings(self):
        return [
            coating
            for coatings in [
                self.get_coatings_for_subfamily(subfamily)
                for subfamily in self.get_product_families_heat_protected_glass()
            ]
            for coating in coatings
        ]

    def coating_is_produceable(self, subfamily: str, coating: str) -> bool:
        """
        Check if the coating is available for the given subfamily.
        """
        return (
            subfamily in self.get_product_families_heat_protected_glass()
            and coating in self.get_coatings_for_subfamily(subfamily)
        )

    def get_eclaz_plants(self) -> list[str]:
        """
        Get the plants that have the coating ECLAZ
        """
        return self.get_coatings_for_subfamily(subfamily="ECLAZ")

    def productionline_has_eclaz_coating(self, subfamily: str) -> bool:
        """
        Check if the production line has the coating for the given subfamily
        """
        return subfamily in self.get_eclaz_plants()
