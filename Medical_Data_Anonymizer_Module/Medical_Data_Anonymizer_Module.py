import os
import slicer
from slicer.ScriptedLoadableModule import *
import logging
import ctk
import qt
import pandas as pd
import uuid

class Medical_Data_Anonymizer_Module(ScriptedLoadableModule):
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Medical Data Anonymizer Module"
        self.parent.categories = ["Examples"]
        self.parent.dependencies = []
        self.parent.contributors = ["Jonas Bianchi"]
        self.parent.helpText = """This module anonymizes text files using Presidio."""
        self.parent.acknowledgementText = """Developed using Slicer resources."""

class Medical_Data_Anonymizer_ModuleWidget(ScriptedLoadableModuleWidget):

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        # Input Directory Section
        self.inputLabel = qt.QLabel("Files to be Anonymized")
        self.layout.addWidget(self.inputLabel)

        self.inputDirectoryButton = ctk.ctkPathLineEdit()
        self.inputDirectoryButton.filters = ctk.ctkPathLineEdit.Dirs
        self.inputDirectoryButton.setToolTip("Select the directory containing the files to be anonymized.")
        self.layout.addWidget(self.inputDirectoryButton)

        # Output Directory Section
        self.outputLabel = qt.QLabel("Output Anonymized Files")
        self.layout.addWidget(self.outputLabel)

        self.outputDirectoryButton = ctk.ctkPathLineEdit()
        self.outputDirectoryButton.filters = ctk.ctkPathLineEdit.Dirs
        self.outputDirectoryButton.setToolTip("Select the directory to save the anonymized files.")
        self.layout.addWidget(self.outputDirectoryButton)

        # Anonymization Options Section
        self.optionsLabel = qt.QLabel("<b>Anonymization Options:</b>")
        self.layout.addWidget(self.optionsLabel)

        # Create checkboxes for different entity types
        self.entityCheckboxes = {}
        
        entities = [
            ("PERSON", "Names (patients, doctors)", True),
            ("PHONE_NUMBER", "Phone Numbers", True),
            ("EMAIL_ADDRESS", "Email Addresses", True),
            ("DATE_TIME", "Dates and Times", True),
            ("LOCATION", "Addresses and Locations", True),
            ("US_SSN", "Social Security Numbers", True),
            ("MEDICAL_LICENSE", "Medical License Numbers", True),
            ("US_DRIVER_LICENSE", "Driver's License Numbers", False),
            ("CREDIT_CARD", "Credit Card Numbers", False),
            ("US_BANK_NUMBER", "Bank Account Numbers", False),
            ("IP_ADDRESS", "IP Addresses", False),
            ("URL", "URLs/Websites", False),
        ]

        for entity_type, description, default_checked in entities:
            checkbox = qt.QCheckBox(description)
            checkbox.setChecked(default_checked)
            checkbox.setToolTip(f"Anonymize {entity_type}")
            self.entityCheckboxes[entity_type] = checkbox
            self.layout.addWidget(checkbox)

        # Advanced Options Collapsible Section
        self.advancedCollapsible = ctk.ctkCollapsibleButton()
        self.advancedCollapsible.text = "Advanced Options"
        self.advancedCollapsible.collapsed = True
        self.layout.addWidget(self.advancedCollapsible)
        
        advancedLayout = qt.QFormLayout(self.advancedCollapsible)

        # Anonymization method dropdown
        self.anonymizationMethodCombo = qt.QComboBox()
        self.anonymizationMethodCombo.addItem("Replace with Label", "replace")
        self.anonymizationMethodCombo.addItem("Redact (Remove)", "redact")
        self.anonymizationMethodCombo.addItem("Hash", "hash")
        self.anonymizationMethodCombo.addItem("Mask", "mask")
        self.anonymizationMethodCombo.setToolTip("Choose how to anonymize detected entities")
        advancedLayout.addRow("Anonymization Method:", self.anonymizationMethodCombo)

        # Score threshold slider
        self.scoreThresholdSlider = ctk.ctkSliderWidget()
        self.scoreThresholdSlider.minimum = 0.0
        self.scoreThresholdSlider.maximum = 1.0
        self.scoreThresholdSlider.value = 0.5
        self.scoreThresholdSlider.singleStep = 0.05
        self.scoreThresholdSlider.setToolTip("Confidence threshold for entity detection (0.0-1.0). Higher = more strict.")
        advancedLayout.addRow("Confidence Threshold:", self.scoreThresholdSlider)

        # Install Dependencies Button
        self.installDependenciesButton = qt.QPushButton("Install Dependencies")
        self.installDependenciesButton.toolTip = "Install Presidio and required dependencies."
        self.layout.addWidget(self.installDependenciesButton)
        self.installDependenciesButton.connect('clicked(bool)', self.install_dependencies)

        # Anonymize Button
        self.anonymizeButton = qt.QPushButton("Anonymize Files")
        self.anonymizeButton.toolTip = "Run the anonymization process."
        self.anonymizeButton.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        self.layout.addWidget(self.anonymizeButton)
        self.anonymizeButton.connect('clicked(bool)', self.onAnonymizeButton)

        # Progress bar
        self.progressBar = qt.QProgressBar()
        self.progressBar.setVisible(False)
        self.layout.addWidget(self.progressBar)

        # Status label
        self.statusLabel = qt.QLabel("")
        self.layout.addWidget(self.statusLabel)

        # Add vertical spacer
        self.layout.addStretch(1)

    def install_dependencies(self):
        try:
            self.statusLabel.setText("Installing dependencies...")
            slicer.app.processEvents()
            
            # Install Presidio
            slicer.util.pip_install('presidio-analyzer')
            slicer.util.pip_install('presidio-anonymizer')
            slicer.util.pip_install('pandas')
            slicer.util.pip_install('python-docx')
            
            # Download spaCy language model (Presidio requires it)
            import spacy
            try:
                spacy.load("en_core_web_lg")
            except:
                spacy.cli.download("en_core_web_lg")

            self.statusLabel.setText("Dependencies installed successfully!")
            
            # Notify user to restart Slicer
            qt.QMessageBox.information(
                slicer.util.mainWindow(),
                'Restart Required',
                'Dependencies have been installed. Please restart 3D Slicer to complete the installation.'
            )
        except Exception as e:
            self.statusLabel.setText(f"Error installing dependencies: {str(e)}")
            qt.QMessageBox.critical(
                slicer.util.mainWindow(),
                'Installation Error',
                f'Error installing dependencies: {str(e)}'
            )

    def onAnonymizeButton(self):
        # Validate inputs
        if not self.inputDirectoryButton.currentPath:
            qt.QMessageBox.warning(
                slicer.util.mainWindow(),
                'Input Required',
                'Please select an input directory.'
            )
            return

        if not self.outputDirectoryButton.currentPath:
            qt.QMessageBox.warning(
                slicer.util.mainWindow(),
                'Input Required',
                'Please select an output directory.'
            )
            return

        # Check dependencies
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_anonymizer import AnonymizerEngine
            import docx
        except ImportError:
            qt.QMessageBox.warning(
                slicer.util.mainWindow(),
                'Dependencies Not Installed',
                'Please install the dependencies first by clicking the "Install Dependencies" button and restart 3D Slicer.'
            )
            return

        # Get selected entities
        selected_entities = [entity for entity, checkbox in self.entityCheckboxes.items() if checkbox.isChecked()]
        
        if not selected_entities:
            qt.QMessageBox.warning(
                slicer.util.mainWindow(),
                'No Options Selected',
                'Please select at least one anonymization option.'
            )
            return

        # Get anonymization method
        anonymization_method = self.anonymizationMethodCombo.currentData
        score_threshold = self.scoreThresholdSlider.value

        # Initialize Presidio
        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()

        input_folder = self.inputDirectoryButton.currentPath
        output_folder = self.outputDirectoryButton.currentPath
        csv_file_path = os.path.join(output_folder, "file_mappings.csv")

        # Get list of files
        docx_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.endswith(".docx") and not file.startswith("~$"):
                    docx_files.append(os.path.join(root, file))

        if not docx_files:
            qt.QMessageBox.information(
                slicer.util.mainWindow(),
                'No Files Found',
                'No .docx files found in the selected directory.'
            )
            return

        # Show progress bar
        self.progressBar.setVisible(True)
        self.progressBar.setMaximum(len(docx_files))
        self.progressBar.setValue(0)

        # Run the anonymization process
        file_mappings = []

        for idx, input_file_path in enumerate(docx_files):
            try:
                file = os.path.basename(input_file_path)
                self.statusLabel.setText(f"Processing: {file}")
                slicer.app.processEvents()

                unique_id = str(uuid.uuid4())
                doc = docx.Document(input_file_path)
                full_text = "\n".join([para.text for para in doc.paragraphs])

                # Anonymize using Presidio
                anonymized_text = self.anonymize_text_presidio(
                    full_text, 
                    analyzer, 
                    anonymizer, 
                    selected_entities,
                    anonymization_method,
                    score_threshold
                )

                # Create new document
                new_doc = docx.Document()
                for line in anonymized_text.split("\n"):
                    new_doc.add_paragraph(line)

                new_file_name = f"{unique_id}.docx"
                output_docx_path = os.path.join(output_folder, new_file_name)
                new_doc.save(output_docx_path)

                file_mappings.append({
                    "Original File Name": file,
                    "Anonymized File Name": new_file_name,
                    "UUID": unique_id
                })

                logging.info(f"Anonymized file created: {output_docx_path}")

            except Exception as e:
                logging.error(f"Error processing {file}: {e}")
                file_mappings.append({
                    "Original File Name": file,
                    "Anonymized File Name": "ERROR",
                    "UUID": f"Error: {str(e)}"
                })

            self.progressBar.setValue(idx + 1)
            slicer.app.processEvents()

        # Save mappings
        mappings_df = pd.DataFrame(file_mappings)
        if not mappings_df.empty:
            mappings_df.to_csv(csv_file_path, index=False)
            self.statusLabel.setText(f"Complete! Processed {len(docx_files)} files.")
            logging.info(f"Anonymization complete. File mappings saved to {csv_file_path}.")
            
            qt.QMessageBox.information(
                slicer.util.mainWindow(),
                'Anonymization Complete',
                f'Successfully processed {len(docx_files)} files.\n\nMappings saved to:\n{csv_file_path}'
            )
        else:
            self.statusLabel.setText("No valid files were processed.")
            logging.info("No valid files were processed. CSV file not created.")

        self.progressBar.setVisible(False)

    def anonymize_text_presidio(self, text, analyzer, anonymizer, entities, method, score_threshold):
        """
        Anonymize text using Presidio
        
        Parameters:
        - text: The text to anonymize
        - analyzer: Presidio AnalyzerEngine instance
        - anonymizer: Presidio AnonymizerEngine instance
        - entities: List of entity types to detect
        - method: Anonymization method ('replace', 'redact', 'hash', 'mask')
        - score_threshold: Confidence threshold for detection
        """
        try:
            # Analyze text
            results = analyzer.analyze(
                text=text,
                language='en',
                entities=entities,
                score_threshold=score_threshold
            )

            # Define operators based on method
            if method == "replace":
                # Replace with entity type label
                operators = {}
            elif method == "redact":
                # Remove the entity completely
                from presidio_anonymizer.entities import OperatorConfig
                operators = {entity: OperatorConfig("redact") for entity in entities}
            elif method == "hash":
                # Replace with hash
                from presidio_anonymizer.entities import OperatorConfig
                operators = {entity: OperatorConfig("hash") for entity in entities}
            elif method == "mask":
                # Mask with asterisks
                from presidio_anonymizer.entities import OperatorConfig
                operators = {entity: OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 100, "from_end": False}) for entity in entities}
            else:
                operators = {}

            # Anonymize
            anonymized = anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                operators=operators if operators else None
            )

            return anonymized.text

        except Exception as e:
            logging.error(f"Error in Presidio anonymization: {e}")
            return text  # Return original text if anonymization fails

class Medical_Data_Anonymizer_ModuleLogic(ScriptedLoadableModuleLogic):
    pass

class Medical_Data_Anonymizer_ModuleTest(ScriptedLoadableModuleTest):
    pass
