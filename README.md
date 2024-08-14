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
- **Jonas Bianchi** - Developer and Maintainer

## License
This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE.txt) file for details.

## Acknowledgments
This module leverages the [spaCy](https://spacy.io/) library and its `en_core_web_sm` pre-trained model for natural language processing. We acknowledge the spaCy team for their powerful and user-friendly NLP tools.
