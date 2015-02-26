from marshmallow import Schema, fields


class SampleModelSchema(Schema):
    int_col = fields.Integer()
    dec_col = fields.Number()


class SampleModelRequiredSchema(Schema):
    int_col = fields.Integer(required=True)
    dec_col = fields.Number(required=True)