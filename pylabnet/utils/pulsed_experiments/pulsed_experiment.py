
import os
from pylabnet.hardware.awg.zi_hdawg import Driver, Sequence, AWGModule
from pylabnet.utils.zi_hdawg_pulseblock_handler.zi_hdawg_pb_handler import DIOPulseBlockHandler

class PulsedExperiment():
    """ Wrapper class for Pulsed experiments using the ZI HDAWG.
    This class conveniently allows for the generation and the AWG upload of
    DIO pulse-sequences.
    """

    def get_templates(self, template_directory="sequence_templates"):
        """Look in sequence template folder and return list of templates."""

        # Get all relevant files template files
        current_directory = os.path.dirname(os.path.realpath(__file__))

        template_directory = os.path.join(current_directory, template_directory)

        files = [file for file in os.listdir(template_directory)
            if  '.seqct' in file and '__init__.py' not in file
        ]

        files_trimmed = [filename.replace('.seqct', '') for filename in files]

        return files_trimmed

    def replace_placeholders(self):
        """Replace all sequence placeholders with values."""
        self.seq.replace_placeholders(self.placeholder_dict)
        self.hd.log.info("Replaced placeholders.")

    def replace_dio_commands(self, pulseblock, dio_command_number):
        """Replace all DIO-waveform placeholders with DIO waveform commands.

        :pulseblock: Pulseblock object
        :dio_command_number: (int) Index designating which DIO-waveform placeholder
        needs to be replaced.
        """

        if self.iplot:
            from pylabnet.utils.pulseblock.pb_iplot import iplot
            iplot(pulseblock)

        # Instanciate pulseblock handler.
        pb_handler = DIOPulseBlockHandler(
            pb = pulseblock,
            assignment_dict=self.assignment_dict,
            hd=self.hd
        )

        # Generate .seqc instruction set which represents pulse sequence.
        dig_pulse_sequence = pb_handler.get_dio_sequence()

        # Construct replacement dict
        dio_replacement_dict = {
            f"{self.dio_seq_identifier}{dio_command_number}": dig_pulse_sequence
        }

        # Replace DIO waveform placeholder.
        self.seq.replace_placeholders(dio_replacement_dict)
        self.hd.log.info("Replaced DIO sequence(s).")


    def prepare_sequence(self):
        """Prepares sequence by replacing all placeholders and DIO-placeholders."""

        # First replace the standard placeholder.
        if self.placeholder_dict is not None:
            self.replace_placeholders()

        # Then replace the DIO commands:
        for i, pulseblock in enumerate(self.pulseblocks):
            self.replace_dio_commands(pulseblock, i)

    def prepare_awg(self, awg_number):
        """ Create AWG instance, uploads sequence and configures DIO output bits

        :awg_nuber: (int) Core number of AWG to be started.
        """

        # Create an instance of the AWG Module.
        awg = AWGModule(self.hd, awg_number)
        awg.set_sampling_rate('2.4 GHz') # Set 2.4 GHz sampling rate.

        self.hd.log.info("Preparing to upload sequence.")

        # Upload sequence.
        if awg is not None:
            awg.compile_upload_sequence(self.seq)

        for pulseblock in self.pulseblocks:
            # Instanciate pulseblock handler.
            pb_handler = DIOPulseBlockHandler(
                pb = pulseblock,
                assignment_dict=self.assignment_dict,
                hd=self.hd
            )
            pb_handler.setup_hd()

        return awg

    def get_ready(self, awg_number):
        """Prepare AWG for sequence execution.

        This function will generate the sequence based on the placeholders and the
        pulseblocks, upload it to the AWG and configure the DIO output bits.
        """
        self.prepare_sequence()
        return self.prepare_awg(awg_number)

    def __init__(self, pulseblocks, assignment_dict, hd, placeholder_dict=None,
    use_template=True, template_name='base_dig_pulse', sequence_string=None,
    dio_seq_identifier='dig_sequence', template_directory="sequence_templates", iplot=True):
        """ Initilizes pulseblock experiment

        :hd: Instance of ZI AWG Driver
        :pulseblock_objects: Single Pulseblock object or list of Pulseblock
                    objects.
        :assignment_dict: Assigning channels to DIO output bins.
        :placeholder_dict: Dictionary containing placeholder names and values for the .seqct file.
        :use_template: (bool) If True, look for .seqc template, if false, use
            sequence_string .
        :template_name: (str) Name of the .seqct template file (must be stored in sequence_template_folders)
        :sequence_string: (str) .seqc sequence if no template sequence is used.
        :dio_seq_identifier: (str) Placeholder within .seqct files to be replaced with DIO sequences.
        :template_directory: Folder where to look for .seqct templates.
        :iplot: If True, sequences will be plotted.
        """

        # Ugly typecasting
        if type(pulseblocks) != list:
            self.pulseblocks = [pulseblocks]
        else:
            self.pulseblocks = pulseblocks

        self.assignment_dict = assignment_dict
        self.hd = hd
        self.template_name = template_name
        self.sequence_string = sequence_string
        self.placeholder_dict = placeholder_dict
        self.dio_seq_identifier = dio_seq_identifier
        self.iplot = iplot

        # Check if template is available, and store it.
        if use_template:
            templates = self.get_templates(template_directory)
            if not template_name in templates:
                error_msg = f"Template name {template_name} not found. Available templates are {templates}."
                self.hd.log.error(error_msg)

            template_filepath =  os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                template_directory,
                f'{template_name}.seqct'
            )
            sequence_string =  open(template_filepath, 'r').read()
            self.hd.log.info(f"Using template {template_name}.seqc")

        # If no template given, use argument input.
        else:
            sequence_string = sequence_string
            self.hd.log.info("Using user input sequence.")

        # Initialize sequence object.
        self.seq = Sequence(
            hdawg_driver = hd,
            sequence = sequence_string,
        )








