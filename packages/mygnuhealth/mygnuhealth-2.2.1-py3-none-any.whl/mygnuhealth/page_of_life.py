####################################################################
#   Copyright (C) 2020-2024 Luis Falcon <falcon@gnuhealth.org>
#   Copyright (C) 2020-2024 GNU Solidario <health@gnusolidario.org>
#   License: GPL v3+
#   Please read the COPYRIGHT and LICENSE files of the package
####################################################################

import datetime
from tinydb import Query
from uuid import uuid4
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from mygnuhealth.lang import tr
from mygnuhealth.core import (check_date, PageOfLife,
                              vardb, CodeNameMap,
                              bol_domain_formatter,
                              bol_genetic_info_formatter)


class PoL():
    """This class creates a new page in the user's Book of Life

        Attributes:
        -----------
            wrongDate: Signal to emit when an invalid date is found
            todayDate: Property with current date

        Methods:
        --------
            get_domains: Returns main domains (medical, social, biographical..)

    """

    domain = CodeNameMap(
        mapinfo=[{'code': 'medical', 'name': tr.N_('Medical')},
                 {'code': 'social', 'name': tr.N_('Social')},
                 {'code': 'biographical', 'name': tr.N_('Biographical')},
                 {'code': 'lifestyle', 'name': tr.N_('Lifestyle')},
                 {'code': 'other', 'name': tr.N_('Other')}
                 ])

    medical_context = CodeNameMap(
        mapinfo=[
            {'code': 'health_condition', 'name': tr.N_('Health Condition')},
            {'code': 'encounter', 'name': tr.N_('Encounter')},
            {'code': 'procedure', 'name': tr.N_('Procedure')},
            {'code': 'self_monitoring', 'name': tr.N_('Self monitoring')},
            {'code': 'immunization', 'name': tr.N_('Immunization')},
            {'code': 'prescription', 'name': tr.N_('Prescription')},
            {'code': 'surgery', 'name': tr.N_('Surgery')},
            {'code': 'hospitalization', 'name': tr.N_('Hospitalization')},
            {'code': 'lab', 'name': tr.N_('Lab test')},
            {'code': 'dx_imaging', 'name': tr.N_('Dx Imaging')},
            {'code': 'genetics', 'name': tr.N_('Genetics')},
            {'code': 'family', 'name': tr.N_('Family history')},
        ])

    social_context = CodeNameMap(
        mapinfo=[
            {'code': 'social_gradient',
             'name': tr.N_('Social Gradient / Equity')},
            {'code': 'stress', 'name': tr.N_('Stress')},
            {'code': 'early_life_development',
             'name': tr.N_('Early life development')},
            {'code': 'social_exclusion',
             'name': tr.N_('Social exclusion')},
            {'code': 'working_conditions',
             'name': tr.N_('Working conditions')},
            {'code': 'education', 'name': tr.N_('Education')},
            {'code': 'physical_environment',
             'name': tr.N_('Physical environment')},
            {'code': 'unemployment', 'name': tr.N_('Unemployment')},
            {'code': 'social_support', 'name': tr.N_('Social Support')},
            {'code': 'addiction', 'name': tr.N_('Addiction')},
            {'code': 'food', 'name': tr.N_('Food')},
            {'code': 'transportation', 'name': tr.N_('Transportation')},
            {'code': 'health_services', 'name': tr.N_('Health services')},
            {'code': 'family_functionality',
             'name': tr.N_('Family functionality')},
            {'code': 'family_violence', 'name': tr.N_('Family violence')},
            {'code': 'bullying', 'name': tr.N_('Bullying')},
            {'code': 'war', 'name': tr.N_('War')},
            {'code': 'misc', 'name': tr.N_('Misc')},
        ])

    lifestyle_context = CodeNameMap(
        mapinfo=[
            {'code': 'physical_activity', 'name': tr.N_('Physical Activity')},
            {'code': 'nutrition', 'name': tr.N_('Nutrition')},
            {'code': 'sleep', 'name': tr.N_('Sleep')},
            {'code': 'social_activities', 'name': tr.N_('Social Activities')},
        ])

    biographical_context = CodeNameMap(
        mapinfo=[
            {'code': 'birth', 'name': tr.N_('Birth')},
            {'code': 'death', 'name': tr.N_('Death')},
            {'code': 'misc', 'name': tr.N_('Misc')}
        ])

    other_context = CodeNameMap(
        mapinfo=[
            {'code': 'misc', 'name': tr.N_('Misc')},
        ])

    relevance = CodeNameMap(
        mapinfo=[
            {'code': 'normal', 'name': tr.N_('Normal')},
            {'code': 'important', 'name': tr.N_('Important')},
            {'code': 'critical', 'name': tr.N_('Critical')},
        ])

    @classmethod
    def get_domain_names(cls):
        return cls.domain.get_names()

    @classmethod
    def get_domain_name(cls, domain_code):
        return cls.domain.get_name(domain_code)

    @classmethod
    def get_domain_code(cls, domain_name):
        return cls.domain.get_code(domain_name)

    @classmethod
    def get_context_name(cls, context_code):
        context_name = None
        for ctx in [cls.social_context,
                    cls.medical_context,
                    cls.lifestyle_context,
                    cls.biographical_context,
                    cls.other_context]:
            context_name = ctx.get_name(context_code)
            if context_name:
                break

        return context_name

    @classmethod
    def get_context_names(cls, domain_name):
        domain_code = cls.get_domain_code(domain_name)
        if domain_code == 'social':
            domain_contexts = cls.social_context
        if domain_code == 'medical':
            domain_contexts = cls.medical_context
        if domain_code == 'lifestyle':
            domain_contexts = cls.lifestyle_context
        if domain_code == 'biographical':
            domain_contexts = cls.biographical_context
        if domain_code == 'other':
            domain_contexts = cls.other_context

        return domain_contexts.get_names()

    @classmethod
    def update_context_names(cls, domain_name):
        """ Set the value of the domain from the selection"""
        domain_code = cls.get_domain_code(domain_name)

        if domain_code == 'social':
            pol_context = cls.social_context
        if domain_code == 'medical':
            pol_context = cls.medical_context
        if domain_code == 'lifestyle':
            pol_context = cls.lifestyle_context
        if domain_code == 'biographical':
            pol_context = cls.biographical_context
        if domain_code == 'other':
            pol_context = cls.other_context

        return pol_context.get_names()

    @classmethod
    def domain_context_is_genetic(cls, context_name):
        context_code = cls.get_context_code(context_name)
        return context_code == 'genetics'

    @classmethod
    def get_context_code(cls, context_name):
        context_code = None
        # Should we add domain argument to let method faster?
        for ctx in [cls.social_context,
                    cls.medical_context,
                    cls.lifestyle_context,
                    cls.biographical_context,
                    cls.other_context]:
            context_code = ctx.get_code(context_name)
            if context_code:
                break

        return context_code

    @classmethod
    def get_relevance_names(cls):
        return cls.relevance.get_names()

    @classmethod
    def get_relevance_code(cls, relevance_name):
        return cls.relevance.get_code(relevance_name)

    @classmethod
    def bol_domain_formatter(cls, args):
        domain_code, context_code = args[0], args[1]
        return '{0} ({1})'.format(
            cls.get_domain_name(domain_code) or '',
            cls.get_context_name(context_code) or '')

    def get_rsinfo(self):
        return self.rsinfo

    def get_date():
        """
        Returns the date packed into an array (day,month,year, hour, min)
        """
        rightnow = datetime.datetime.now()
        dateobj = []
        dateobj.append(str(rightnow.day))
        dateobj.append(str(rightnow.month))
        dateobj.append(str(rightnow.year))
        dateobj.append(str(rightnow.hour))
        dateobj.append(str(rightnow.minute))
        return dateobj

    def new_page(data):
        page_id = str(uuid4())

        pol_vals = {
            'page': page_id,
            'page_date': data['page_date'],
            'domain': data['domain'],
            'context': data['context'],
            'relevance': data['relevance'],
            'privacy': data['privacy'],
            'summary': data['summary'],
            'info': data['info']
        }
        if (data['context'] == 'genetics'):
            pol_vals.update({'genetic_info': data['genetic_info']})

        PageOfLife.create_pol(PageOfLife, pol_vals)

    def checkSNP(rs):
        rsinfo = {}
        if rs:
            Rsnp = Query()
            res = vardb.search(Rsnp.dbsnp == rs)
            if len(res) > 0:
                res = res[0]
                rsinfo = {
                    'rsid': res['dbsnp'],
                    'gene': res['gene'],
                    'aa_change': res['aa_change'],
                    'variant': res['variant'],
                    'protein': res['protein'],
                    'category': res['category'],
                    'disease': res['disease']
                }

                print(rsinfo)
            else:
                print(f"{rs} not found")

        return (rsinfo)

    @classmethod
    def createPage(cls, page_date, domain, context, relevance, private_page,
                   genetic_info, summary, info, use_name=False):
        # Retrieves the information from the initialization form
        # Creates the page from the information on the form
        if use_name:
            domain_code = cls.get_domain_code(domain)
            context_code = cls.get_context_code(context)
            relevance_code = cls.get_relevance_code(relevance)
        else:
            domain_code = domain
            context_code = context
            relevance_code = relevance

        if (page_date):
            if (check_date(page_date[:3])):
                # Sets the page of life date and time
                year, month, day, hour, minute = page_date

                daterp = datetime.datetime(
                    int(year), int(month),
                    int(day), int(hour),
                    int(minute)).isoformat()

                page = {'page_date': daterp,
                        'domain': domain_code,
                        'context': context_code,
                        'relevance': relevance_code,
                        'privacy': private_page,
                        'summary': summary,
                        'info': info
                        }
                if (context_code == 'genetics'):
                    rsinfo = {
                        'rsid': genetic_info[0],
                        'gene': genetic_info[1],
                        'aa_change': genetic_info[2],
                        'variant': genetic_info[3],
                        'protein': genetic_info[4],
                        'significance': genetic_info[5],
                        'disease': genetic_info[6]
                    }
                    page.update({'genetic_info': rsinfo})
                PoL.new_page(page)
                popup = Popup(
                    title=tr._('Success'),
                    content=Label(
                        text=tr._("Page of Life "
                                  "successfully created!")),
                    size_hint=(0.5, 0.5), auto_dismiss=True)
                popup.open()
                return True

            else:
                popup = Popup(
                    title=tr._('Error'),
                    content=Label(
                        text=tr._("Wrong date")),
                    size_hint=(0.5, 0.5), auto_dismiss=True)
                popup.open()

    @classmethod
    def bol_genetic_info_formatter(cls, args):
        rsid = str(args.get('rsid')) or ''
        gene = str(args.get('gene')) or ''
        aa_change = str(args.get('aa_change')) or ''
        variant = str(args.get('variant')) or ''
        protein = str(args.get('protein')) or ''
        significance = str(args.get('significance')) or ''
        disease = str(args.get('disease')) or ''

        return (tr._("RefSNP ID: ") + rsid + '\n' +
                tr._("Gene: ") + gene + '\n' +
                tr._("AA_change: ") + aa_change + '\n' +
                tr._("Natural variant: ") + variant + '\n' +
                tr._("Protein ID: ") + protein + '\n' +
                tr._("Significance: ") + significance + '\n' +
                tr._("Disease: ") + disease)


bol_genetic_info_formatter.add(
    'genetic_info', PoL.bol_genetic_info_formatter)


bol_domain_formatter.add(
    'domain', PoL.bol_domain_formatter)
