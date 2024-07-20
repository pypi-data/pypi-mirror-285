from sqlalchemy import MetaData, Table, func, select

from rov_db_access.gis.models import ResultsVector


def st_transform(item, srid):
    return func.ST_Transform(item, srid)


def st_intersects(geom1, geom2):
    return func.ST_Intersects(geom1, geom2)


def st_intersection(geom1, geom2):
    return func.ST_Intersection(geom1, geom2)


def st_union(geom1, geom2):
    return func.ST_Union(geom1, geom2)


def st_difference(geom1, geom2):
    return func.ST_Difference(geom1, geom2)


def st_sym_difference(geom1, geom2):
    return func.ST_SymDifference(geom1, geom2)


def st_geomfromtext(wkt):
    return func.ST_GeomFromText(wkt)


def st_geojson(geom):
    return func.ST_AsGeoJSON(geom)


OPERATIONS = {
    'intersection': st_intersection,
    'union': st_union,
    'difference': st_difference,
    'symmetric_difference': st_sym_difference,
}


class OperableItem:
    def __init__(self):
        self.common_srid = 32719
        self.display_srid = 4326

    def operate(self, other, operation: str):
        raise NotImplementedError

    def base_query_maker(self, operation: str, geom1, geom2):
        op_function = OPERATIONS[operation]
        base_query = st_transform(
            op_function(
                st_transform(geom1, self.common_srid),
                st_transform(geom2, self.common_srid)
            ), self.display_srid
        )

        return base_query

    def where_conditions_maker(self, operation: str, geom1, geom2):
        raise NotImplementedError


class OpWkt(OperableItem):
    def __init__(self, wkt: str):
        super().__init__()
        self.wkt = wkt

    def add_srid(self, srid: int):
        self.wkt = f"SRID={srid};{self.wkt}"

    def operate(self, other, operation: str):
        return other.operated_by_wkt(self.wkt, operation)

    def operated_by_wkt(self, other_wkt: str, operation: str):
        op_function = OPERATIONS[operation]
        query = select(op_function(
            st_geomfromtext(self.wkt),
            st_geomfromtext(other_wkt)
        ))
        return query

    def __str__(self):
        return self.wkt


class OpVectorResult(OperableItem):
    def __init__(self, output_data_id: int):
        super().__init__()
        self.output_data_id = output_data_id
        self.table = ResultsVector
        self.geom_column = self.table.geom

    def where_conditions_maker(self, operation: str, geom1, geom2):
        if operation == 'intersection' or operation == 'difference':
            where_conditions = [
                st_intersects(
                    st_transform(geom1, self.common_srid),
                    st_transform(geom2, self.common_srid)
                )
            ]
        elif operation == 'symmetric_difference' or operation == 'union':
            where_conditions = []

        return where_conditions

    def operated_by_wkt(self, wkt: str, operation: str):
        base_query = self.base_query_maker(operation, self.geom_column, wkt)

        where_conditions = self.where_conditions_maker(operation, self.geom_column, wkt)
        where_conditions.append(self.table.run_data_id == self.output_data_id)

        query = (
            select(self.table, base_query.label('geom_operation_result'))
            .where(*where_conditions)
        )

        return query


class OpLayer(OperableItem):
    def __init__(self, layer: str, geodata_engine):
        super().__init__()
        self.layer = layer
        self.metadata = MetaData(schema='infrastructure')
        self.table = Table(layer, self.metadata, autoload_with=geodata_engine)
        self.geom_column = self.table.c.geom

    def where_conditions_maker(self, operation: str, geom1, geom2):
        if operation == 'intersection' or operation == 'difference':
            where_conditions = [
                st_intersects(
                    st_transform(geom1, self.common_srid),
                    st_transform(geom2, self.common_srid)
                )
            ]
        elif operation == 'symmetric_difference':
            where_conditions = [
                ~st_intersects(
                    st_transform(geom1, self.common_srid),
                    st_transform(geom2, self.common_srid)
                )
            ]
        elif operation == 'union':
            where_conditions = []

        return where_conditions

    def operated_by_wkt(self, wkt: str, operation: str):
        base_query = self.base_query_maker(operation, self.geom_column, wkt)

        where_conditions = self.where_conditions_maker(operation, self.geom_column, wkt)

        columns = [col for col in self.table.c]

        query = (
            select(*columns, base_query.label('geom_operation_result'))
            .where(*where_conditions)
        )

        return query
