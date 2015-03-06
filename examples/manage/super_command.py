from seth import command


class SuperCommand(command.Command):
    name = 'super_command'
    args = (
        (("-v", "--verbose"), {}),
    )

    def run(self, verbose):
        print "Option verbose set to: {0}".format(verbose)
        print "This is me - super command"
        print "This is my env:"
        print self.env
        print "These are my setting:"
        print self.settings