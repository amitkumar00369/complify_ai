data ={
  "workflow_source": "SABER",
  "workflow_name": "PCOC",
  "product_name": "ACRYLIC TOP COAT",
  "risk_level": "medium",
  "required_documents": [
    "technical report",
    "photos and labels",
    "sdoc",
    "pid"
  ],
  "workflow_sequence": [
    "product identification",
    "technical report submission",
    "risk assessment",
    "sdoc submission",
    "label verification",
    "pcoc approval"
  ],
  "approval_outputs": [
    "pcoc certificate"
  ]
}

dmo ={
  "product_name": "",

  "regulation_summary": {
    "possible_hs_codes": [],
    "technical_regulations": [],
    "standards": []
  },

  "saber_response": {
    "workflow_type": "",

    "risk_level": "",

    "required_documents": [
      {
        "document_name": "",
        "purpose": ""
      }
    ],

    "workflow_sequence": [],

    "approval_outputs": []
  },

  "ksa_saleem_response": {
    "authority": "",

    "programs": [],

    "applicable_categories": [],

    "technical_requirements": {},

    "required_documents": [
      {
        "document_name": "",
        "purpose": ""
      }
    ],

    "required_features": [],

    "frequency_requirements": [],

    "approval_conditions": []
  }
}


from datetime import datetime


def build_compliance_response(extracted_data: dict) -> dict:

    pcoc = extracted_data.get("pcoc_data", {})
    reports = extracted_data.get("products_file_info", [])

    technical_report_available = False
    labeling_verified = False
    risk_assessment_available = False

    standards = set()
    programs = set()
    frequencies = set()
    approval_conditions = set()
    required_features = set()
    applicable_categories = set()

    technical_requirements = {
        "protection_class": [],
        "ip_rating": [],
        "voltage": [],
        "power_rating": []
    }

    workflow_sequence = []
    approval_outputs = []

    # ---------------------------------------------------
    # Parse report text
    # ---------------------------------------------------

    for file in reports:

        text = (file.get("text") or "").lower()

        # Technical report
        if "test report" in text or "cb scheme" in text:
            technical_report_available = True
            programs.add("IECEE CB Scheme")

        # Label verification
        if "marking and instructions" in text:
            labeling_verified = True

        # Risk assessment
        if "abnormal operation" in text:
            risk_assessment_available = True

        # Standards
        if "iec 60335-2-36" in text:
            standards.add("IEC 60335-2-36")

        if "iec 60335-1" in text:
            standards.add("IEC 60335-1")

        if "iec 60335-2-42" in text:
            standards.add("IEC 60335-2-42")

        # Protection class
        if "class i" in text:
            technical_requirements["protection_class"].append("Class I")

        # IP Rating
        if "ipx4" in text:
            technical_requirements["ip_rating"].append("IPX4")

        # Frequency
        if "50/60hz" in text:
            frequencies.append("50/60Hz")

        # Voltage
        if "380-415v" in text:
            technical_requirements["voltage"].append("380-415V")

        # Power
        if "21,4kw" in text or "21.4kw" in text:
            technical_requirements["power_rating"].append("21.4kW")

        # Commercial category
        if "commercial use" in text:
            applicable_categories.add(
                "Commercial Electrical Cooking Appliances"
            )

        # Approval conditions
        if "stationary appliance" in text:
            approval_conditions.add(
                "Appliance must be permanently installed"
            )

    # ---------------------------------------------------
    # Workflow
    # ---------------------------------------------------

    workflow_sequence = [
        "Product Registration",
        "Technical Document Review",
        "PCoC Issuance",
        "Shipment Certificate Approval",
        "Customs Clearance"
    ]

    approval_outputs = [
        "PCoC Certificate",
        "Shipment Certificate",
        "SABER Approval"
    ]

    # ---------------------------------------------------
    # Final response
    # ---------------------------------------------------

    response = {
        "product_name": pcoc.get("product_name", ""),

        "regulation_summary": {
            "possible_hs_codes": [
                pcoc.get("hs_code")
            ] if pcoc.get("hs_code") else [],

            "technical_regulations": [
                pcoc.get("technical_regulation")
            ] if pcoc.get("technical_regulation") else [],

            "standards": list(standards)
        },

        "saber_workflow": {
            "workflow_type": "SABER Conformity Workflow",

            "risk_level": "Medium",

            "required_documents": [
                {
                    "document_name": "Commercial Invoice",
                    "purpose": "Product import verification"
                },
                {
                    "document_name": "Test Report",
                    "purpose": "Technical compliance validation"
                },
                {
                    "document_name": "PCoC Certificate",
                    "purpose": "SABER conformity approval"
                }
            ],

            "workflow_sequence": workflow_sequence,

            "approval_outputs": approval_outputs
        },

        "ksa_saleem_requirements": {
            "authority": "SASO",

            "programs": list(programs),

            "applicable_categories": list(applicable_categories),

            "technical_requirements": technical_requirements,

            "required_documents": [
                {
                    "document_name": "CB Test Report",
                    "purpose": "Electrical safety verification"
                },
                {
                    "document_name": "Label Artwork",
                    "purpose": "Marking compliance verification"
                }
            ],

            "required_features": list(required_features),

            "frequency_requirements": list(frequencies),

            "approval_conditions": list(approval_conditions)
        },

        "compliance_evidence": {
            "technical_report_available": technical_report_available,
            "risk_assessment_available": risk_assessment_available,
            "labeling_verified": labeling_verified
        },

        "metadata": {
            "source": "SABER Compliance Engine",
            "source_folder": extracted_data.get("folder_name", ""),
            "confidence_score": 0.92,
            "generated_at": datetime.utcnow().isoformat()
        }
    }

    return response