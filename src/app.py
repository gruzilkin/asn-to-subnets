import subprocess
from typing import List

from fastapi.responses import PlainTextResponse
from netaddr import IPNetwork, cidr_merge
from fastapi import FastAPI, Query

app = FastAPI()

# get subnets from whois command
def get_subnets_from_command(asn):
    command_output = subprocess.check_output(
        f"whois -h whois.radb.net — '-i origin {asn}' | grep ^route:",
        shell=True,
        text=True
    )

    subnets = []
    for line in command_output.strip().split('\n'):
        _, subnet = line.split(':')
        subnets.append(subnet.strip())
    return subnets

# merge overlapping subnets
def merge_subnets(subnets):
    ip_networks = [IPNetwork(subnet) for subnet in subnets]
    merged_subnets = cidr_merge(ip_networks)
    return merged_subnets

@app.get("/")
async def root(asn: List[str] = Query(None)):
    if not asn:
        return PlainTextResponse(status_code=400, content="No AS numbers provided with asn get parameter")

    for as_number in asn:
        if not as_number.startswith("AS") or not as_number[2:].isdigit():
            return PlainTextResponse(status_code=400, content=f"Invalid AS number: {as_number}")

    subnets = []
    for as_number in asn:
        for subnet in get_subnets_from_command(as_number):
            subnets.append(subnet)

    merged_subnets = merge_subnets(subnets)
    result = "\n".join([str(subnet) for subnet in merged_subnets])
    return PlainTextResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)