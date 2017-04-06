"""
    ================================================
    :mod:`observers` -- Algorithm monitoring methods
    ================================================
    
    This module provides pre-defined observers for evolutionary computations.
    
    All observer functions have the following arguments:
    
    - *population* -- the population of Individuals
    - *num_generations* -- the number of elapsed generations
    - *num_evaluations* -- the number of candidate solution evaluations
    - *args* -- a dictionary of keyword arguments    
    
    .. note::
    
       The *population* is really a shallow copy of the actual population of
       the evolutionary computation. This means that any activities like
       sorting will not affect the actual population.
    
    .. Copyright 2012 Aaron Garrett

    .. Permission is hereby granted, free of charge, to any person obtaining a copy
       of this software and associated documentation files (the "Software"), to deal
       in the Software without restriction, including without limitation the rights
       to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
       copies of the Software, and to permit persons to whom the Software is
       furnished to do so, subject to the following conditions:

    .. The above copyright notice and this permission notice shall be included in
       all copies or substantial portions of the Software.

    .. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
       IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
       FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
       AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
       LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
       OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
       THE SOFTWARE.       
        
    .. module:: observers
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import email
import inspyred
import math
import os
import smtplib
import time


    

def default_observer(population, num_generations, num_evaluations, args):
    """Do nothing."""    
    pass
    

def best_observer(population, num_generations, num_evaluations, args):
    """Print the best individual in the population to the screen.
    
    This function displays the best individual in the population to 
    the screen. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    print("Best Individual: {0}\n".format(str(max(population))))
    
    
def stats_observer(population, num_generations, num_evaluations, args):
    """Print the statistics of the evolutionary computation to the screen.
    
    This function displays the statistics of the evolutionary computation
    to the screen. The output includes the generation number, the current
    number of evaluations, the maximum fitness, the minimum fitness, 
    the average fitness, and the standard deviation.
    
    .. note::
    
       This function makes use of the ``inspyred.ec.analysis.fitness_statistics`` 
       function, so it is subject to the same requirements.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    stats = inspyred.ec.analysis.fitness_statistics(population)
    worst_fit = '{0:>10}'.format(stats['worst'])[:10]
    best_fit = '{0:>10}'.format(stats['best'])[:10]
    avg_fit = '{0:>10}'.format(stats['mean'])[:10]
    med_fit = '{0:>10}'.format(stats['median'])[:10]
    std_fit = '{0:>10}'.format(stats['std'])[:10]
            
    print('Generation Evaluation      Worst       Best     Median    Average    Std Dev')
    print('---------- ---------- ---------- ---------- ---------- ---------- ----------')
    print('{0:>10} {1:>10} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10}\n'.format(num_generations, 
                                                                             num_evaluations, 
                                                                             worst_fit, 
                                                                             best_fit, 
                                                                             med_fit, 
                                                                             avg_fit, 
                                                                             std_fit))


def population_observer(population, num_generations, num_evaluations, args):
    """Print the current population of the evolutionary computation to the screen.
    
    This function displays the current population of the evolutionary 
    computation to the screen in fitness-sorted order. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    population.sort(reverse=True)
    print('----------------------------------------------------------------------------')
    print('                            Current Population')
    print('----------------------------------------------------------------------------')
    for ind in population:
        print(str(ind))
    print('----------------------------------------------------------------------------')
    
    
def file_observer(population, num_generations, num_evaluations, args):
    """Print the output of the evolutionary computation to a file.
    
    This function saves the results of the evolutionary computation
    to two files. The first file, which by default is named 
    'inspyred-statistics-file-<timestamp>.csv', contains the basic
    generational statistics of the population throughout the run
    (worst, best, median, and average fitness and standard deviation
    of the fitness values). The second file, which by default is named
    'inspyred-individuals-file-<timestamp>.csv', contains every individual
    during each generation of the run. Both files may be passed to the
    function as keyword arguments (see below).
    
    The format of each line of the statistics file is as follows::
    
       generation number, population size, worst, best, median, average, standard deviation

    The format of each line of the individuals file is as follows::
    
       generation number, individual number, fitness, string representation of candidate
    
    .. note::
    
       This function makes use of the ``inspyred.ec.analysis.fitness_statistics`` 
       function, so it is subject to the same requirements.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *statistics_file* -- a file object (default: see text)
    - *individuals_file* -- a file object (default: see text) 
    
    """
    try:
        statistics_file = args['statistics_file']
    except KeyError:
        statistics_file = open('inspyred-statistics-file-{0}.csv'.format(time.strftime('%m%d%Y-%H%M%S')), 'w')
        args['statistics_file'] = statistics_file
    try:
        individuals_file = args['individuals_file']
    except KeyError:
        individuals_file = open('inspyred-individuals-file-{0}.csv'.format(time.strftime('%m%d%Y-%H%M%S')), 'w')
        args['individuals_file'] = individuals_file

    stats = inspyred.ec.analysis.fitness_statistics(population)
    worst_fit = stats['worst']
    best_fit = stats['best']
    avg_fit = stats['mean']
    med_fit = stats['median']
    std_fit = stats['std']
    
    statistics_file.write('{0}, {1}, {2}, {3}, {4}, {5}, {6}\n'.format(num_generations, len(population), worst_fit, best_fit, med_fit, avg_fit, std_fit))
    for i, p in enumerate(population):
        individuals_file.write('{0}, {1}, {2}, {3}\n'.format(num_generations, i, p.fitness, str(p.candidate)))
    statistics_file.flush()
    individuals_file.flush()
    

def archive_observer(population, num_generations, num_evaluations, args):
    """Print the current archive to the screen.
    
    This function displays the current archive of the evolutionary 
    computation to the screen. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
       
    """
    archive = args['_ec'].archive
    print('----------------------------------------------------------------------------')
    print('                         Archive ({0:5} individuals)'.format(len(archive)))
    print('----------------------------------------------------------------------------')
    for a in archive:
        print(a)
    print('----------------------------------------------------------------------------')

    
class EmailObserver(object):
    """Email the population statistics, individuals, and optional file observer data.
    
    This callable class allows information about the current generation
    to be emailed to a user. This is useful when dealing with computationally
    expensive optimization problems where the evolution must progress over
    hours or days. The ``generation_step`` attribute can be set to an integer
    greater than 1 to ensure that emails are only sent on generations that are
    multiples of the step size.
    
    .. note::
    
       This function makes use of the ``inspyred.ec.analysis.fitness_statistics`` 
       function, so it is subject to the same requirements.
    
    A typical instantiation of this class would be the following::
    
        import getpass
        usr = raw_input("Enter your username: ")
        pwd = getpass.getpass("Enter your password: ")
        email_observer = EmailObserver(usr, pwd, "my.mail.server")
        email_observer.from_address = "me@here.com"
        email_observer.to_address = "you@there.com" # or ["you@there.com", "other@somewhere.com"]
        email_observer.subject = "My custom subject"
        email_observer.generation_step = 10 # Send an email every 10th generation
    
    Public Attributes:
    
    - *username* -- the mail server username
    - *password* -- the mail server password
    - *server* -- the mail server URL or IP address string
    - *port* -- the mail server port as an integer
    - *from_address* -- the email address of the sender
    - *to_address* -- the (possibly list of) email address(es) of the receiver(s)
    - *subject* -- the subject of the email (default 'inspyred observer report')
    - *max_attachment* -- the maximum allowable size, in MB, of attachments
      (default 20 MB)
    - *generation_step* -- the step size for when a generation's information 
      should be emailed (default 1)
    
    """
    def __init__(self, username, password, server, port=587):
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.generation_step = 1
        self.max_attachment = 20
        self.subject = "inspyred observer report"
        self.__name__ = self.__class__.__name__
        
    def _send_mail(self, fromaddr, toaddr, subject, text, attachments=None):
        if not isinstance(toaddr, (list, tuple)):
            toaddr = [toaddr]
        msg = email.MIMEMultipart.MIMEMultipart('related')
        msg['From'] = fromaddr
        msg['To'] = ','.join(toaddr)
        msg['Subject'] = subject
        body = email.MIMEMultipart.MIMEMultipart('alternative')
        body.attach(email.MIMEText.MIMEText(text, 'plain'))
        html = '<html><body><tt>{0}</tt></body></html>'.format(text.replace(' ', '&nbsp;').replace('\n', '<br/>'))
        body.attach(email.MIMEText.MIMEText(html, 'html'))
        msg.attach(body)
        if attachments is not None:
            if not isinstance(attachments, (list, tuple)):
                attachments = [attachments]
            for file in attachments:
                part = email.MIMEBase.MIMEBase('application', 'octet-stream')
                fp = open(file, 'rb')
                part.set_payload(fp.read())
                fp.close()
                email.Encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(file)))
                msg.attach(part)
        mail_server = smtplib.SMTP(self.server, self.port)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(self.username, self.password)
        mail_server.sendmail(fromaddr, toaddr, msg.as_string())
        mail_server.quit()
        
    def __call__(self, population, num_generations, num_evaluations, args):
        if num_generations % self.generation_step == 0:
            stats = inspyred.ec.analysis.fitness_statistics(population)
            worst_fit = '{0:>10}'.format(stats['worst'])[:10]
            best_fit = '{0:>10}'.format(stats['best'])[:10]
            avg_fit = '{0:>10}'.format(stats['mean'])[:10]
            med_fit = '{0:>10}'.format(stats['median'])[:10]
            std_fit = '{0:>10}'.format(stats['std'])[:10]
            
            body = 'Generation Evaluation      Worst       Best     Median    Average    Std Dev\n'
            body += '---------- ---------- ---------- ---------- ---------- ---------- ----------\n'
            body += '{0:>10} {1:>10} {2:>10} {3:>10} {4:>10} {5:>10} {6:>10}\n'.format(num_generations, 
                                                                                       num_evaluations, 
                                                                                       worst_fit, 
                                                                                       best_fit, 
                                                                                       med_fit, 
                                                                                       avg_fit, 
                                                                                       std_fit)
            body += '----------------------------------------------------------------------------\n'
            for p in population:
                body += str(p) + '\n'
            body += '----------------------------------------------------------------------------\n'
            total_size = 0
            files = []
            stats = args.get("statistics_file", None) 
            inds = args.get("individuals_file", None)
            for file in [stats, inds]:
                if file is not None:
                    files.append(file.name)
                    total_size += os.path.getsize(file.name)
            if total_size > (self.max_attachment * 1048576):
                files = None
            self._send_mail(self.from_address, self.to_address, self.subject, body, files)    
        
        
def plot_observer(population, num_generations, num_evaluations, args):    
    """Plot the output of the evolutionary computation as a graph.
    
    This function plots the performance of the EC as a line graph 
    using matplotlib and numpy. The graph consists of a blue line 
    representing the best fitness, a green line representing the 
    average fitness, and a red line representing the median fitness.
    It modifies the keyword arguments variable 'args' by including an
    entry called 'plot_data'.
    
    If this observer is used, the calling script should also import
    the matplotlib library and should end the script with::
    
        matplotlib.pyplot.show()
    
    Otherwise, the program may generate a runtime error.
    
    .. note::
    
       This function makes use of the matplotlib and numpy libraries.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    import matplotlib.pyplot as plt
    import numpy
    
    stats = inspyred.ec.analysis.fitness_statistics(population)
    best_fitness = stats['best']
    worst_fitness = stats['worst']
    median_fitness = stats['median']
    average_fitness = stats['mean']
    colors = ['black', 'blue', 'green', 'red']
    labels = ['average', 'median', 'best', 'worst']
    data = []
    if num_generations == 0:
        plt.ion()
        data = [[num_evaluations], [average_fitness], [median_fitness], [best_fitness], [worst_fitness]]
        lines = []
        for i in range(4):
            line, = plt.plot(data[0], data[i+1], color=colors[i], label=labels[i])
            lines.append(line)
        # Add the legend when the first data is added.
        plt.legend(loc='lower right')
        args['plot_data'] = data
        args['plot_lines'] = lines
        plt.xlabel('Evaluations')
        plt.ylabel('Fitness')
    else:
        data = args['plot_data']
        data[0].append(num_evaluations)
        data[1].append(average_fitness)
        data[2].append(median_fitness)
        data[3].append(best_fitness)
        data[4].append(worst_fitness)
        lines = args['plot_lines']
        for i, line in enumerate(lines):
            line.set_xdata(numpy.array(data[0]))
            line.set_ydata(numpy.array(data[i+1]))
        args['plot_data'] = data
        args['plot_lines'] = lines
    ymin = min([min(d) for d in data[1:]])
    ymax = max([max(d) for d in data[1:]])
    yrange = ymax - ymin
    plt.xlim((0, num_evaluations))
    plt.ylim((ymin - 0.1*yrange, ymax + 0.1*yrange))
    plt.draw()
