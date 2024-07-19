# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class StockProductionLot(models.Model):
    _name = "stock.production.lot"
    _inherit = ["stock.production.lot"]

    @api.depends(
        "stock_move_line_ids",
        "stock_move_line_ids.date",
        "stock_move_line_ids.move_id.state",
        "tracking",
    )
    def _compute_serial_number_in_date(self):
        for rec in self:
            serial_number_in_date = False
            if rec.tracking == "serial":
                criteria = [("lot_id", "=", rec.id), ("state", "=", "done")]

                first_move_line_id = self.env["stock.move.line"].search(
                    criteria, order="date, id", limit=1
                )
                serial_number_in_date = first_move_line_id.date
            rec.serial_number_in_date = serial_number_in_date

    tracking = fields.Selection(related="product_id.tracking", store=True)
    stock_move_line_ids = fields.One2many(
        comodel_name="stock.move.line",
        inverse_name="lot_id",
        string="Stock Move Lines",
        copy=False,
    )
    serial_number_in_date = fields.Datetime(
        string="Incoming Date",
        compute="_compute_serial_number_in_date",
        compute_sudo=False,
        store=False,
    )
