from datetime import datetime
from pytz import timezone
from rich import align
from rich.console import Console
from rich.table import Table
import csv
import json

wallets = []
with open("my-wallets.csv") as f:
    for row in csv.DictReader(f):
        wallets.append(row)

known_addresses = {
    '0x737901bea3eeb88459df9ef1be8ff3ae1b42a2ba': 'Aztec: Bridge',
    '0xFF1F2B4ADb9dF6FC8eAFecDcbF96A2B351680455': 'Aztec: Connect',
    '0xD64791E747188b0e5061fC65b56Bf20FeE2e3321': 'Aztec: Sequencer',
}
known_addresses = {k.lower(): v for k, v in known_addresses.items()}

labeled_transactions = []

# Find transactions from/to known addresses.
with open("transactions.json") as f:
    transactions = json.load(f)
    for tx in transactions:
        if tx['from'].lower() in known_addresses or tx['to'].lower() in known_addresses:
            labeled_transactions.append(tx)

# Sort by timestamp.
labeled_transactions = sorted(labeled_transactions, key=lambda tx: -int(tx['timeStamp']))

def address_label(address):
    if address in known_addresses:
        return f"💚 {known_addresses[address]}"
    for wallet in wallets:
        if wallet['address'].lower() == address.lower():
            return f"💙 {wallet['address'][0:6]}...{wallet['address'][-4:]}"
    return address

table = Table(title="Transactions to known addresses", show_lines=True)
table.add_column("Time")
table.add_column("From")
table.add_column("To")
table.add_column("Value")
table.add_column("Hash", overflow="ellipsis")
for tx in labeled_transactions:
    positive = tx['from'].lower() in known_addresses
    color = "green" if positive else "red"
    sign = "+" if positive else "-"

    # Icon to represent normal/token/internal transaction.
    icon = "💸"
    if 'tokenSymbol' in tx:
        icon = "🪙"
    elif 'traceId' in tx:
        icon = "🔗"

    table.add_row(
        datetime.fromtimestamp(int(tx['timeStamp']), tz=timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S"),
        address_label(tx['from']),
        address_label(tx['to']),
        "[{color}]{sign}{value:.2f} {symbol} [/]".format(
            color=color,
            sign=sign,
            value=float(tx['value']) / 1e18,
            symbol=tx['tokenSymbol'] if 'tokenSymbol' in tx else 'ETH',
        ),
        f"{icon}{tx['hash']}",
    )
Console().print(table)
