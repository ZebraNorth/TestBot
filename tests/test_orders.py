from tests.hexcorp import as_drone
from testbot import embed, expect, text, text_channel


@as_drone
async def test_report() -> None:
    '''
    Ensure that report_order adds an order.
    '''

    ch = text_channel('hive-orders-reporting')

    # Add a new order.
    await ch.send('hc!report "Test orders" 1')
    await expect(
        ch,
        text(
            'If safe and willing to do so, Drone 3521 Activate.\n'
            'Drone 3521 will elaborate on its exact tasks before proceeding with them.'
            )
        )

    # Attempt to add a new order while one is already in progress.
    await ch.send('hc!report_order "Second order" 1')
    await expect(ch, text('HexDrone #3521 is already undertaking the Test orders protocol.'))


@as_drone
async def test_report_complete() -> None:
    '''
    Ensure that report_order adds an order.
    '''

    ch = text_channel('hive-orders-reporting')

    # Add a new order.  This may or may not succeed, depending on if an order is already in progress.
    await ch.send('hc!report "Test orders" 1')

    await ch.send('hc!report_complete "Test orders" 3521 Do some stuff')

    expected_fields = [
        {'name': 'Drone ID', 'value': '3521'},
        {'name': 'Issuer', 'value': '3521'},
        {'name': 'Objective', 'value': 'Test orders'},
        {'name': 'Report Details', 'value': 'Do some stuff'},
        {'name': 'Report Complete', 'value': 'End report.'},
    ]

    await expect(ch, embed('Summary of activity for 3521', *expected_fields))
