import json
import sys
import os
from datetime import datetime
import uuid

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dal.integrations.gemini_client import GeminiClientSingleton
from core.entities.protocol_entities import Protocol, ProtocolStep

# 1. Initialize Gemini client
client = GeminiClientSingleton().client

response_schema = {
    "type": "object",
    "properties": {
        "protocol": {
            "type": "object",
            "properties": {
                "protocol_id": {"type": "string"},
                "document_id": {"type": "string"},
                "protocol_name": {"type": "string"},
                "description": {"type": "string"},
                "created_by_user_id": {"type": "string"},
                "created_at": {"type": "string"},
                "updated_at": {"type": "string"}
            },
            "required": ["protocol_id", "document_id", "protocol_name", "created_at", "updated_at"]
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "protocol_step_id": {"type": "string"},
                    "protocol_id": {"type": "string"},
                    "step_number": {"type": "integer"},
                    "step_name": {"type": "string"},
                    "instruction": {"type": "string"},
                    "expected_duration_minutes": {"type": "integer"},
                    "created_at": {"type": "string"},
                    "updated_at": {"type": "string"}
                },
                "required": ["protocol_step_id", "protocol_id", "step_number", "step_name", "instruction", "created_at", "updated_at"]
            }
        }
    },
    "required": ["protocol", "steps"]
}

# 2. Assume you already extracted text from the image (OCR result)
ocr_text = """
General Protocol for Western Blotting

Protocol

Bulletin 6376

Key Solutions and Reagents

Lysis buffer: Radioimmunoprecipitation
assay buffer (RIPA buffer)
50 mM Tris-HCl, pH 8.0
150 mM NaCl
1% Nonidet P-40 (NP-40) or 0.1% Triton X-100
0.5% sodium deoxycholate
0.1% sodium dodecyl sulphate (SDS)
1 mM sodium orthovanadate
1 mM NaF
Protease inhibitors tablet (Roche)

Loading buffer: 2x Laemmli buffer
4% SDS
10% 2-mercaptoethanol
20% glycerol
0.004% bromophenol blue
0.125 M Tris-HCI
Check the pH and adjust to pH 6.8 if necessary.

Running buffer: Tris/Glycine/SDS
25 mM Tris
190 mM glycine
0.1% SDS

Transfer buffer
25 mM Tris
190 mM glycine
20% methanol
For proteins larger than 80 kD, we recommend that
SDS be included at a final concentration of 0.1%.

Ponceau S staining buffer
0.2% (w/v) Ponceau S
5% glacial acetic acid

Tris-buffered saline with Tween 20 (TBST) buffer
20 mM Tris, pH 7.5
150 mM NaCl
0.1% Tween 20

Blocking buffer
3% bovine serum albumin (BSA) in TBST

Stripping buffer
20 ml 10% SDS
12.5 ml 0.5 M Tris HCI, pH 6.8
67.5 ml ultrapure water
0.8 ml 2-mercaptoethanol

Procedure

Sample prep (based on a typical cell culture scenario)
1. Place the cell culture dish in ice and wash the cells with
ice-cold Tris-buffered saline (TBS).
2. Aspirate the TBS, then add ice-cold RIPA buffer (1 ml per
100 mm dish).
3. Scrape adherent cells off the dish using a cold plastic cell
scraper and gently transfer the cell suspension into a
precooled microcentrifuge tube.
4. Maintain constant agitation for 30 min at 4°C.
5. If necessary, sonicate 3 times for 10-15 sec to complete
cell lysis and shear DNA to reduce sample viscosity.
6. Spin at 16,000 x g for 20 min in a 4°C precooled centrifuge.
7. Gently remove the centrifuge tube and place it on ice.
Transfer the supernatant to a fresh tube, also kept on ice,
and discard the pellet.
8. Remove a small volume (10-20 µl) of lysate to perform
a protein assay. Determine the protein concentration
foreach cell lysate.
9. If necessary, aliquot the protein samples for long-term
storage at -20°C. Repeated freeze and thaw cycles cause
protein degradation and should be avoided.
10. Take 20 µg of each sample and add an equal volume
of 2x Laemmli sample buffer.
11. Boil each cell lysate in sample buffer at 95°C for 5 min.
12. Centrifuge at 16,000 x g in a microcentrifuge for 1 min.

BIO-RAD

---

General Protocol for Western Blotting

Protein separation by gel electrophoresis
1. Load equal amounts of protein (20 µg) into the wells of
a mini (8.6 x 6.7 cm) or midi (13.3 x 8.7 cm) format SDS-
PAGE gel, along with molecular weight markers.
2. Run the gel for 5 min at 50 V.
3. Increase the voltage to 100–150 V to finish the run
in about 1 hr.

Gel percentage selection depends on the size of the protein of
interest. A 4–20% gradient gel separates proteins of all sizes
very well. For details, please refer to the Protein Blotting Guide,
bulletin 2895.

Transferring the protein from the gel to the membrane
1. Place the gel in 1x transfer buffer for 10–15 min.
2. Assemble the transfer sandwich and make sure no air
bubbles are trapped in the sandwich. The blot should
be on the cathode and the gel on the anode.
3. Place the cassette in the transfer tank and place an ice
block in the tank.
4. Transfer overnight in a coldroom at a constant current
of 10 mA.
Note: Transfer can also be done at 100 V for 30 min–2 hr, but the method
needs to be optimized for proteins of different sizes.

Antibody incubation
1. Briefly rinse the blot in water and stain it with Ponceau S
solution to check the transfer quality.
2. Rinse off the Ponceau S stain with three washes
with TBST.
3. Block in 3% BSA in TBST at room temperature for 1 hr.
4. Incubate overnight in the primary antibody solution against
the target protein at 4°C.
Note: The antibody should be diluted in the blocking buffer according to
the manufacturer’s recommended ratio. Primary antibody may be applied
to the blot for 1–3 hr at room temperature depending on antibody quality
and performance.
5. Rinse the blot 3–5 times for 5 min with TBST.
6. Incubate in the HRP-conjugated secondary antibody
solution for 1 hr at room temperature.
Note: The antibody can be diluted using 5% skim milk in TBST.
7. Rinse the blot 3–5 times for 5 min with TBST.

Imaging and data analysis
1. Apply the chemiluminescent substrate to the blot
according to the manufacturer’s recommendation.
2. Capture the chemiluminescent signals using a CCD
camera-based imager.
Note: The use of film is not recommended in this step because of its
limited dynamic range.
3. Use image analysis software to read the band intensity
of the target proteins.

Stripping and reprobing
1. Warm the buffer to 50°C.
2. Add the buffer to the membrane in a container designated
for stripping. Incubate at 50°C for up to 45 min with
some agitation.
3. Rinse the blot under running water for 1 hr.
4. Transfer the membrane to a clean container, wash
5 times for 5 min with TBST.
5. Block in 3% BSA in TBST at room temperature for 1 hr.
6. Incubate overnight in the primary antibody solution
(against the loading control protein) at 4°C.
Note: The antibody should be diluted in the blocking buffer at the
manufacturer’s recommended ratio.
7. Rinse the blot 3–5 times for 5 min with TBST.
8. Incubate in the HRP-conjugated secondary antibody
solution for 1 hr at room temperature.
Note: The antibody can be diluted using 5% skim milk in TBST.
9. Rinse the blot 3–5 times for 5 min with TBST.

Imaging and data analysis
1. Apply the chemiluminescent substrate to the blot following
the manufacturer’s suggestions.
2. Capture the chemiluminescent signals using a CCD
camera-based imager.
Note: The use of film is not recommended in this step because of its
limited dynamic range.
3. Use image analysis software to read the band intensity
of the loading control proteins.
4. Use the loading control protein levels to normalize the
target protein levels.

Nonidet is a trademark of Shell International Petroleum Co. Triton is a trademark
of Dow Chemical Company. Tween is a trademark of ICI Americas Inc.

BIO-RAD
Bio-Rad
Laboratories, Inc.

Life Science
Group
Web site bio-rad.com USA 1 800 424 6723 Australia 61 2 9914 2800 Austria 43 1 877 89 01 177 Belgium 32 (0)3 710 53 00 Brazil 55 11 3065 7550
Canada 1 905 364 3435 China 86 21 6169 8500 Czech Republic 420 241 430 532 Denmark 45 44 52 10 00 Finland 358 09 804 22 00
France 33 01 47 95 69 65 Germany 49 89 31 884 0 Hong Kong 852 2789 3300 Hungary 36 1 459 6100 India 91 124 4029300
Israel 972 03 963 6050 Italy 39 02 216091 Japan 81 3 6361 7000 Korea 82 2 3473 4460 Mexico 52 555 488 7670 The Netherlands 31 (0)318 540 666
New Zealand 64 9 415 2280 Norway 47 23 38 41 30 Poland 48 22 331 99 99 Portugal 351 21 472 7700 Russia 7 495 721 14 04
Singapore 65 6415 3188 South Africa 27 (0) 861 246 723 Spain 34 91 590 5200 Sweden 46 08 555 12700 Switzerland 41 026674 55 05
Taiwan 886 2 2578 7189 Thailand 66 2 651 8311 United Arab Emirates 971 4 8187300 United Kingdom 44 020 8328 2000

Bulletin 6376 Ver C US/EG
17-0657 0517 Sig 1216
"""

doc_id = uuid.uuid4()
proto_id = uuid.uuid4()
now = datetime.now()

"""response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents=[
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        f"Given the following protocol text, produce JSON matching the schema.\n"
                        f"Use the following pre-assigned IDs:\n"
                        f"document_id: {doc_id}\n"
                        f"protocol_id: {proto_id}\n"
                        f"Use current timestamp {now} for all created_at and updated_at fields.\n"
                        f"Text:\n{ocr_text}"
                    )
                }
            ],
        }
    ],
    config={
        "response_mime_type": "application/json",
        "response_schema": response_schema,
    },
)"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        f"Given the following protocol text, produce JSON matching the schema for each step of the protocol.\n"
                        f"There will often be a step with sub steps; in that case treat every step as its own step number.\n"
                        f"If there is a time range given vs an exact time, select the upper bound of the time range.\n"
                        f"Use the following pre-assigned IDs:\n"
                        f"document_id: {doc_id}\n"
                        f"protocol_id: {proto_id}\n"
                        f"Use current timestamp {now} for all created_at and updated_at fields.\n"
                        f"Text:\n{ocr_text}"
                    )
                }
            ],
        }
    ],
    config={
        "response_mime_type": "application/json",
        "response_schema": list[ProtocolStep],
    },
)

response_protcol = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        {
            "role": "user",
            "parts": [
                {
                    "text": (
                        f"Given the following protocol text, produce JSON matching the schema for the protocol.\n"
                        f"The description should be a concise summary of what is accomplished in the experiment.\n"
                        f"Use the following pre-assigned IDs:\n"
                        f"document_id: {doc_id}\n"
                        f"protocol_id: {proto_id}\n"
                        f"Use current timestamp {now} for all created_at and updated_at fields.\n"
                        f"Text:\n{ocr_text}"
                    )
                }
            ],
        }
    ],
    config={
        "response_mime_type": "application/json",
        "response_schema": Protocol,
    },
)

response_protcol_text = response_protcol.text
print(response_protcol_text)
with open("protocol_output.txt", "w", encoding="utf-8") as file:
    file.write(response_protcol_text)


# 5. Parse and load into Pydantic models
data = response.text
print(data)

with open("protocol_steps_output.txt", "w", encoding="utf-8") as file:
    file.write(data)