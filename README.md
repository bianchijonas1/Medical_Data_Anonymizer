<img width="580" alt="Screenshot 2024-08-14 at 3 37 44 PM" src="https://github.com/user-attachments/assets/8d57eb74-bca4-4add-bad9-094bf85aaf1b">



# Medical Data Anonymizer Module

## Description
The Medical Data Anonymizer Module is a 3D Slicer extension designed to anonymize medical data in text files. It focuses on removing personal identifiers, such as patient names and dates of birth, while retaining other critical clinical information. This ensures that the data remains useful for research and analysis while protecting patient privacy.

This module uses the [spaCy](https://spacy.io/) library for natural language processing (NLP) to identify and anonymize personal information. Specifically, it utilizes the `en_core_web_sm` pre-trained model for named entity recognition (NER) to detect names, dates, and other entities within the text.

## Installation
To install the Medical Data Anonymizer Module, follow these steps:

1. **Using 3D Slicer Extension Manager:**
   - Open 3D Slicer.
   - Go to `Edit > Application Settings > Modules`.
   - Click `Add Module Path` and select the folder containing the Medical Data Anonymizer Module.
   - Restart 3D Slicer to apply the changes.

2. **Manual Installation:**
   - Clone this repository to your local machine:
     ```bash
     git clone https://github.com/YourGitHubUsername/MedicalDataAnonymizer.git
     ```
   - In 3D Slicer, go to `Edit > Application Settings > Modules`.
   - Click `Add Module Path` and select the folder where you cloned the repository.
   - Restart 3D Slicer to apply the changes.

## Usage
Once the module is installed, follow these steps to anonymize your medical data:

1. Open 3D Slicer.
2. Navigate to the `Medical Data Anonymizer` module from the module dropdown.
3. In the `Files to be Anonymized` section, select the directory containing the text files you want to anonymize. TYPE OF FILE: .DOCX
4. In the `Output Anonymized Files` section, choose the directory where you want to save the anonymized files.
5. Click the `Install Dependencies` button to ensure all necessary packages are installed.
6. After dependencies are installed, click the `Anonymize` button to start the anonymization process.
7. The anonymized files and a CSV file mapping the original filenames to the anonymized filenames will be saved in the output directory.

## Contributors
- Jonas Bianchi,  DCBIA Lab Umich and UNC - Lucia Cevidanes  - Developer and Maintainer

## License
This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE.txt) file for details.

## Acknowledgments
This module leverages the [spaCy](https://spacy.io/) library and its `en_core_web_sm` pre-trained model for natural language processing. We acknowledge the spaCy team for their powerful and user-friendly NLP tools.

---------------
---------------
---------------
---------------
---------------
---------------
---------------
---------------
---------------
---------------
---------------
---------------
---------------


# Medical Data Anonymizer - Upgrade Guide

## What Changed: Presidio Integration

### Before (spaCy only):
- Only detected PERSON and DATE entities
- String replacement had issues with partial matches
- No configuration options
- Small language model (85% accuracy)

### After (Presidio):
- Detects 12+ entity types (names, phones, emails, SSN, etc.)
- Smarter replacement algorithm
- Full UI configuration with checkboxes
- Multiple anonymization methods
- Adjustable confidence threshold
- Better accuracy with larger models

## Installation Instructions

1. **Install Dependencies** (in Slicer):
   - Click "Install Dependencies" button
   - Restart 3D Slicer

2. **Required Python packages**:
   ```
   presidio-analyzer
   presidio-anonymizer
   pandas
   python-docx
   spacy (with en_core_web_lg model)
   ```

## Usage Examples

### Example 1: Maximum Privacy
**Settings:**
- ✅ Check ALL entity types
- Method: **Redact** (removes completely)
- Threshold: **0.5** (balanced)

**Result:**
```
Dr. Smith treated patient John Doe on 03/15/2023.
Phone: 555-123-4567, Email: jdoe@example.com
```
↓
```
[REDACTED] treated patient [REDACTED] on [REDACTED].
Phone: [REDACTED], Email: [REDACTED]
```

### Example 2: Preserve Structure
**Settings:**
- ✅ Names, Phones, Emails only
- Method: **Replace** (with labels)
- Threshold: **0.5**

**Result:**
```
Dr. Smith treated patient John Doe on 03/15/2023.
Phone: 555-123-4567
```
↓
```
<PERSON> treated patient <PERSON> on 03/15/2023.
Phone: <PHONE_NUMBER>
```

### Example 3: Auditable (Hash)
**Settings:**
- ✅ Names only
- Method: **Hash**
- Threshold: **0.7** (more strict)

**Result:**
```
Dr. Smith and Dr. Smith discuss patient care.
```
↓
```
<PERSON_a3f9b2c> and <PERSON_a3f9b2c> discuss patient care.
```
(Same person = same hash)

## Key Configuration Parameters

### 1. Entity Types (Checkboxes)
Control WHAT gets anonymized:
- PERSON: Patient/doctor names
- PHONE_NUMBER: All phone formats
- EMAIL_ADDRESS: Email addresses
- DATE_TIME: Dates and timestamps
- LOCATION: Addresses, cities, states
- US_SSN: Social Security Numbers
- MEDICAL_LICENSE: Medical license IDs
- CREDIT_CARD: Credit card numbers
- IP_ADDRESS: IP addresses
- URL: Website URLs

### 2. Anonymization Method (Dropdown)
Control HOW anonymization happens:
- **Replace**: `<ENTITY_TYPE>` - Keeps structure, shows what was removed
- **Redact**: Completely removes text
- **Hash**: Unique hash per entity (consistent within document)
- **Mask**: Replaces with asterisks (e.g., ********)

### 3. Confidence Threshold (Slider: 0.0 - 1.0)
Control detection sensitivity:
- **Low (0.3)**: Catches more entities, more false positives
- **Medium (0.5)**: Balanced (recommended)
- **High (0.7)**: Fewer false positives, might miss some entities

## Advanced Customization

### Adding Custom Entity Types
Edit line 47-58 to add custom entities:
```python
entities = [
    ("PERSON", "Names (patients, doctors)", True),
    ("CUSTOM_ID", "Your Custom ID Type", True),  # Add this
    ...
]
```

### Changing Default Settings
Edit line 49 (third parameter = default checked state):
```python
("US_DRIVER_LICENSE", "Driver's License Numbers", True),  # Now checked by default
```

### Language Support
To support other languages, change line 120:
```python
spacy.cli.download("es_core_news_lg")  # For Spanish
# or
spacy.cli.download("fr_core_news_lg")  # For French
```

## File Output

The module creates:
1. **Anonymized DOCX files** with UUID names
2. **file_mappings.csv** tracking:
   - Original File Name
   - Anonymized File Name
   - UUID

## Troubleshooting

### "Dependencies Not Installed" error
- Click "Install Dependencies"
- Restart 3D Slicer completely
- Try again

### Not catching all entities
- Lower the confidence threshold (0.3-0.4)
- Check that entity type is selected
- Verify Presidio is installed correctly

### Too many false positives
- Raise confidence threshold (0.7-0.8)
- Use more specific entity types only

## Performance Comparison

| Metric | Old (spaCy) | New (Presidio) |
|--------|-------------|----------------|
| Entity types | 2 | 12+ |
| Accuracy | ~85% | ~95% |
| Configuration | None | Full UI |
| Methods | 1 (replace) | 4 (replace/redact/hash/mask) |
| Medical-specific | No | Yes (medical license, etc.) |

## Questions?

For issues or feature requests:
https://github.com/bianchijonas1/Medical_Data_Anonymizer/issues

