"""
Script to populate the grants database with opportunities from the PDF
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Grant data extracted from PDF
GRANTS_DATA = [
    {
        'title': 'Black Economic Alliance Entrepreneurs Fund',
        'funder': 'Black Economic Alliance Foundation',
        'description': 'Provides early-stage funding and support to Black and underrepresented founders.',
        'deadline': 'Rolling',
        'funding_amount': 'Equity investments via convertible debt or loans (amounts vary)',
        'eligibility': 'Underserved and overlooked founders in the U.S., especially in financial inclusion, health, sustainability, and storytelling.',
        'url': 'https://foundation.blackeconomicalliance.org/bea-entrepreneurs-fund/',
        'focus_areas': ['Financial Inclusion', 'Health', 'Sustainability', 'Storytelling']
    },
    {
        'title': 'Antler Global Startup Program',
        'funder': 'Antler',
        'description': 'Global VC program helping startups scale with funding and support.',
        'deadline': 'Varies by location',
        'funding_amount': 'Varies',
        'eligibility': 'Early-stage startups and entrepreneurs.',
        'url': 'https://www.antler.co/platform/#apply-now',
        'focus_areas': ['Technology', 'Startups']
    },
    {
        'title': 'We Make Change',
        'funder': 'We Make Change',
        'description': 'Matches impact startups with skilled volunteers to build remote teams for free.',
        'deadline': 'Rolling',
        'funding_amount': 'Volunteer team matching support',
        'eligibility': 'Small and nonprofit businesses.',
        'url': 'https://www.wemakechange.org/',
        'focus_areas': ['Impact', 'Nonprofits']
    },
    {
        'title': 'Santander X Cultivate Small Business Program',
        'funder': 'Santander',
        'description': 'Supports early-stage food entrepreneurs with mentorship, capital, and a 12-week curriculum.',
        'deadline': 'Applications accepted March-June (Fall cohort) and November-January (Spring cohort)',
        'funding_amount': '$20,000',
        'eligibility': 'Food industry businesses with at least 1 year in operation; $25k-$1M in annual revenue; 1-10 full-time employees; based in Rhode Island, Connecticut, Massachusetts, Greater Philadelphia, NYC, or Miami.',
        'url': 'https://ow.ly/UN8P50VomYn',
        'focus_areas': ['Food', 'Entrepreneurship']
    },
    {
        'title': 'Savvy Fellowship',
        'funder': 'Savvy Fellows',
        'description': 'Offers virtual training for aspiring entrepreneurs ready to drive social impact.',
        'deadline': 'Rolling',
        'funding_amount': '12-week virtual fellowship program',
        'eligibility': 'Young professionals aged 40 or younger.',
        'url': 'https://savvyfellows.com/team/',
        'focus_areas': ['Social Impact', 'Entrepreneurship']
    },
    {
        'title': 'Canva Pro For Nonprofits',
        'funder': 'Canva',
        'description': 'Gives nonprofits premium design tools for free.',
        'deadline': 'Rolling',
        'funding_amount': 'Free Canva Pro access',
        'eligibility': 'Registered nonprofits.',
        'url': 'https://www.canva.com/canva-for-nonprofits/',
        'focus_areas': ['Nonprofits', 'Design']
    },
    {
        'title': 'Rémy Martin "This is My City" Microgrant',
        'funder': 'Rémy Martin',
        'description': 'Supports creatives with mentorship and funding to advance their entrepreneurial endeavors.',
        'deadline': 'Not specified',
        'funding_amount': 'Grant and one-on-one mentorship',
        'eligibility': 'Emerging creatives from Atlanta, Chicago, Detroit, and New York City contributing to local culture and communities through entrepreneurship.',
        'url': 'https://ow.ly/cTp050Vg0xA',
        'focus_areas': ['Creative', 'Entrepreneurship']
    },
    {
        'title': 'Amazon Small Business Success Studio',
        'funder': 'Amazon',
        'description': 'Free lessons and advice to help small businesses succeed.',
        'deadline': 'Rolling',
        'funding_amount': 'Free business lessons and tips',
        'eligibility': 'Small business owners and entrepreneurs.',
        'url': 'https://business.amazon.com/en/small-business/success-studio/welcome',
        'focus_areas': ['Small Business', 'Education']
    },
    {
        'title': 'Pollination Project',
        'funder': 'The Pollination Project',
        'description': 'Provides seed funding to grassroots initiatives with a strong social impact focus.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $50,000',
        'eligibility': 'Nonprofits with annual budget under $50,000 and project cost under $40,000.',
        'url': 'https://thepollinationproject.org/apply/',
        'focus_areas': ['Social Impact', 'Grassroots']
    },
    {
        'title': 'Techstars Accelerators',
        'funder': 'Techstars',
        'description': 'Helps startups succeed with funding, mentorship, and global network access.',
        'deadline': 'Various deadlines',
        'funding_amount': '$20,000 for 6% equity',
        'eligibility': 'Companies based in North American time zones.',
        'url': 'https://www.techstars.com/accelerators',
        'focus_areas': ['Technology', 'Startups']
    },
    {
        'title': 'Microsoft for Startups Founders Hub',
        'funder': 'Microsoft',
        'description': 'Helps startups accelerate innovation with Microsoft tech and mentorship resources.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $150,000 in Azure credits',
        'eligibility': 'Startups at any stage.',
        'url': 'https://www.microsoft.com/en-ca/startups',
        'focus_areas': ['Technology', 'Cloud Computing']
    },
    {
        'title': 'American Express Leadership Academy',
        'funder': 'American Express',
        'description': 'Builds nonprofit leaders\' resilience and adaptive capabilities.',
        'deadline': 'Varies by program',
        'funding_amount': 'Leadership training',
        'eligibility': 'Non-profit professionals seeking leadership development.',
        'url': 'https://commonpurpose.org/american-express-leadership-academy#anchor1',
        'focus_areas': ['Leadership', 'Nonprofits']
    },
    {
        'title': 'Morgan Stanley Inclusive & Sustainable Ventures Accelerator',
        'funder': 'Morgan Stanley',
        'description': 'Accelerator programs for startups and nonprofits focusing on inclusivity and sustainability.',
        'deadline': 'Varies',
        'funding_amount': '$250K equity investment or grant',
        'eligibility': 'Startups and nonprofits.',
        'url': 'https://tinyurl.com/bdhk4zf2',
        'focus_areas': ['Sustainability', 'Social Impact']
    },
    {
        'title': 'Goldman Sachs 10,000 Small Businesses',
        'funder': 'Goldman Sachs',
        'description': 'Provides business support and education to help small businesses scale.',
        'deadline': 'Rolling',
        'funding_amount': 'Business education and access to capital',
        'eligibility': 'Businesses making $75,000+ in revenue and operating for 2+ years.',
        'url': 'https://10ksbapply.com/',
        'focus_areas': ['Small Business', 'Education']
    },
    {
        'title': 'Michigan Emerging Technologies Fund',
        'funder': 'Michigan Economic Development Corporation',
        'description': 'Supports high-tech startups in Michigan by matching federal innovation grants.',
        'deadline': 'Varies',
        'funding_amount': 'Matching funds for federal SBIR/STTR grants',
        'eligibility': 'Michigan-based tech startups.',
        'url': 'https://www.mietf.org/#/',
        'focus_areas': ['Technology', 'Innovation']
    },
    {
        'title': 'The Awesome Foundation',
        'funder': 'The Awesome Foundation',
        'description': 'Funds small but impactful ideas monthly with no strings attached.',
        'deadline': 'Monthly',
        'funding_amount': '$1,000',
        'eligibility': 'Anyone with a creative and impactful idea.',
        'url': 'https://www.awesomefoundation.org/en',
        'focus_areas': ['Creative', 'Community']
    },
    {
        'title': 'Diamond Project',
        'funder': 'Diamond Project',
        'description': 'Equips participants with training and tools to launch their own funded business.',
        'deadline': 'Rolling',
        'funding_amount': 'Business training and startup tools',
        'eligibility': 'Aspiring entrepreneurs.',
        'url': 'https://www.diamondproject.org/',
        'focus_areas': ['Entrepreneurship', 'Training']
    },
    {
        'title': 'NASE Growth Grants',
        'funder': 'National Association for the Self-Employed',
        'description': 'Provides self-employed professionals with funding for business development.',
        'deadline': 'Rolling',
        'funding_amount': '$4,000',
        'eligibility': 'Members of the National Association for the Self-Employed (NASE).',
        'url': 'https://www.nase.org/become-a-member/grants-and-scholarships/business-development-grants',
        'focus_areas': ['Self-Employed', 'Business Development']
    },
    {
        'title': 'Etsy Disaster Relief Fund',
        'funder': 'Etsy',
        'description': 'Helps Etsy sellers recover from federally declared disasters.',
        'deadline': 'Rolling',
        'funding_amount': '$2,500',
        'eligibility': 'Etsy sellers affected by natural disasters.',
        'url': 'https://advocacy.etsy.com/etsy-emergency-relief-fund-at-cerf/',
        'focus_areas': ['Disaster Relief', 'Small Business']
    },
    {
        'title': 'Amazon App Store Small Business Accelerator',
        'funder': 'Amazon',
        'description': 'Helps small app developers grow with extra royalties and AWS credits.',
        'deadline': 'Rolling',
        'funding_amount': '10% increased royalty + AWS credits',
        'eligibility': 'Developers earning less than $1 million in annual revenue.',
        'url': 'https://developer.amazon.com/apps-and-games/small-business-program',
        'focus_areas': ['Technology', 'App Development']
    },
    {
        'title': 'HerRise MicroGrant',
        'funder': 'HerRise',
        'description': 'Provides support to under-resourced women entrepreneurs to grow their businesses.',
        'deadline': 'Monthly (last day of each month)',
        'funding_amount': '$1,000',
        'eligibility': 'Women entrepreneurs, including women of color, with community-focused businesses.',
        'url': 'https://lnkd.in/dx5fSKDm',
        'focus_areas': ['Women-Owned', 'Community']
    },
    {
        'title': 'F6S List of Accelerators and Pitch Competitions',
        'funder': 'F6S',
        'description': 'A hub for discovering accelerator programs and pitch competitions across various industries and countries.',
        'deadline': 'Rolling',
        'funding_amount': 'Access to global accelerator listings',
        'eligibility': 'Entrepreneurs and startups worldwide.',
        'url': 'https://www.f6s.com/',
        'focus_areas': ['Startups', 'Accelerators']
    },
    {
        'title': 'Emergent Ventures Grant/Fellowship',
        'funder': 'Mercatus Center',
        'description': 'Funds bold projects aiming to improve society.',
        'deadline': 'Rolling',
        'funding_amount': 'Grants or fellowships',
        'eligibility': 'Entrepreneurs with innovative, scalable ideas.',
        'url': 'https://www.mercatus.org/emergent-ventures',
        'focus_areas': ['Innovation', 'Social Impact']
    },
    {
        'title': 'Founders Factory Africa Gen F Incubator',
        'funder': 'Founders Factory Africa',
        'description': 'Supports systemic impact through innovation across African markets.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $250,000',
        'eligibility': 'Exceptional founders building African tech solutions.',
        'url': 'https://www.foundersfactory.africa/gen-f-eir-initiative',
        'focus_areas': ['Africa', 'Technology']
    },
    {
        'title': 'Grindstone Accelerator',
        'funder': 'Grindstone XL',
        'description': 'Holistic program tailored to company gaps and strategic growth goals.',
        'deadline': 'Rolling',
        'funding_amount': 'Incubation, coaching, mentorship, funding',
        'eligibility': 'African scaleups.',
        'url': 'https://www.grindstonexl.com/grindstone-accelerator',
        'focus_areas': ['Africa', 'Scaleups']
    },
    {
        'title': 'Amber Grants',
        'funder': 'Amber Grants',
        'description': 'Monthly grants for women-owned businesses across sectors.',
        'deadline': 'Monthly',
        'funding_amount': '$10K monthly, $25K year-end',
        'eligibility': 'Women-owned businesses in US or Canada.',
        'url': 'https://ambergrantsforwomen.com/',
        'focus_areas': ['Women-Owned', 'Small Business']
    },
    {
        'title': 'Black Innovation Launchpad',
        'funder': 'DMZ Launchpad',
        'description': 'Designed to develop the next generation of Black Canadian entrepreneurs.',
        'deadline': 'Rolling',
        'funding_amount': 'Free virtual skill-building platform',
        'eligibility': 'Black entrepreneurs.',
        'url': 'https://www.dmzlaunchpad.ca/courses/black-innovation-launchpad',
        'focus_areas': ['Black-Owned', 'Entrepreneurship']
    },
    {
        'title': 'Coralus',
        'funder': 'Coralus',
        'description': 'Leverages undervalued capital for ventures led by women and nonbinary people.',
        'deadline': 'Rolling',
        'funding_amount': 'Collective support, loans, resources',
        'eligibility': 'Ventures led by women and nonbinary people.',
        'url': 'https://www.coralus.world/',
        'focus_areas': ['Women-Owned', 'Nonbinary-Owned']
    },
    {
        'title': 'Dragons Den Auditions',
        'funder': 'CBC',
        'description': 'Season 20 application for pitching to investors on national TV.',
        'deadline': 'Rolling (2025)',
        'funding_amount': 'Chance to pitch for investment',
        'eligibility': 'Canadian entrepreneurs.',
        'url': 'https://www.cbc.ca/dragonsden/auditions',
        'focus_areas': ['Entrepreneurship', 'Canada']
    },
    {
        'title': 'Launchpad for Women Entrepreneurs',
        'funder': 'Launchpad for Women',
        'description': 'Empowers interprovincial growth through tailored training access.',
        'deadline': 'Rolling',
        'funding_amount': 'On-demand learning platform',
        'eligibility': 'Early-stage women entrepreneurs.',
        'url': 'https://www.launchpadforwomen.ca/',
        'focus_areas': ['Women-Owned', 'Education']
    },
    {
        'title': 'Innovate UK KTN',
        'funder': 'Innovate UK KTN',
        'description': 'Centralized UK resource for innovation grants, R&D funding, and business growth opportunities.',
        'deadline': 'Varies by opportunity',
        'funding_amount': 'Various',
        'eligibility': 'UK-based innovators across all sectors.',
        'url': 'https://iuk.ktn-uk.org/opportunities/',
        'focus_areas': ['Innovation', 'UK']
    },
    {
        'title': 'Amazon Black Business Accelerator',
        'funder': 'Amazon',
        'description': 'Helps build equity and growth for Black entrepreneurs through Amazon\'s seller ecosystem.',
        'deadline': 'Rolling',
        'funding_amount': 'Financial support, mentorship, marketing',
        'eligibility': 'Black-owned U.S. businesses selling on Amazon.',
        'url': 'https://sell.amazon.com/programs/black-business-accelerator',
        'focus_areas': ['Black-Owned', 'E-Commerce']
    },
    {
        'title': 'Bank of America Business Education Center',
        'funder': 'Bank of America',
        'description': 'Offers small business training via Cornell partnership and expert-led sessions.',
        'deadline': 'Rolling',
        'funding_amount': 'Free webinars and resources',
        'eligibility': 'Entrepreneurs seeking financial education.',
        'url': 'https://go.bofa.com/BusinessEducationCenter',
        'focus_areas': ['Education', 'Small Business']
    },
    {
        'title': 'Clever Girl Finance',
        'funder': 'Clever Girl Finance',
        'description': 'One of the largest personal finance platforms for women in the U.S.',
        'deadline': 'Rolling',
        'funding_amount': 'Free courses, mentorship, community',
        'eligibility': 'Women seeking financial literacy and business tools.',
        'url': 'https://www.clevergirlfinance.com/#',
        'focus_areas': ['Women-Owned', 'Financial Literacy']
    },
    {
        'title': 'EmpowerHer Grant – Boundless Futures',
        'funder': 'Boundless Futures',
        'description': 'For businesses <3 years old with social impact focus.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $25K reimbursement grant',
        'eligibility': 'U.S.-based women entrepreneurs with social impact businesses.',
        'url': 'https://boundlessfutures.org/our-impact/',
        'focus_areas': ['Women-Owned', 'Social Impact']
    },
    {
        'title': 'First Interstate BancSystem Foundation',
        'funder': 'First Interstate BancSystem Foundation',
        'description': 'Focuses on poverty alleviation and community impact.',
        'deadline': 'Rolling',
        'funding_amount': 'Minimum $2,500',
        'eligibility': 'Nonprofits in 14 western U.S. states.',
        'url': 'https://www.firstinterstatebank.com/company/commitment/grants.php',
        'focus_areas': ['Nonprofits', 'Community Development']
    },
    {
        'title': 'Josephine Collective',
        'funder': 'Josephine Collective',
        'description': 'Streamlined investment process for tech-enabled startups.',
        'deadline': 'Rolling',
        'funding_amount': '$10K–$100K',
        'eligibility': 'US-domiciled, for-profit, tech-enabled startups.',
        'url': 'https://joinjosephine.com/',
        'focus_areas': ['Technology', 'Startups']
    },
    {
        'title': 'Military Entrepreneur Challenge',
        'funder': 'Second Service Foundation',
        'description': 'Nationwide competitions to help military-connected entrepreneurs scale.',
        'deadline': 'Rolling',
        'funding_amount': 'Grant funding + networking',
        'eligibility': 'Veteran, military spouse, or Gold Star Family entrepreneurs.',
        'url': 'https://secondservicefoundation.org/mec/',
        'focus_areas': ['Veterans', 'Entrepreneurship']
    },
    {
        'title': 'Minority Business Circle',
        'funder': 'Minority Business Circle',
        'description': 'Offers business support through community, resources, and funding guidance.',
        'deadline': 'Rolling',
        'funding_amount': 'Grants, loans, discounts',
        'eligibility': 'Diverse founders and small business owners.',
        'url': 'https://minoritybusinesscircle.com/',
        'focus_areas': ['Minority-Owned', 'Small Business']
    },
    {
        'title': 'Mona Access to Capital Initiative',
        'funder': 'Mona Ventures',
        'description': 'Zero-interest loans and support for women, immigrant, and refugee entrepreneurs.',
        'deadline': 'Rolling',
        'funding_amount': 'Zero-interest loans',
        'eligibility': 'All U.S.-based small businesses.',
        'url': 'https://www.mona-ventures.com/mona-capital',
        'focus_areas': ['Women-Owned', 'Immigrant-Owned']
    },
    {
        'title': 'Next 1B Program (McKinsey)',
        'funder': 'McKinsey & Company',
        'description': 'Accelerates growth for mature Black-owned ventures in retail and products.',
        'deadline': 'Rolling',
        'funding_amount': 'Brand support + capital introductions',
        'eligibility': 'Black-owned U.S. consumer brands with $250K-$5M revenue.',
        'url': 'https://www.mckinsey.com/bem/overview/next-1b',
        'focus_areas': ['Black-Owned', 'Retail']
    },
    {
        'title': 'NSF Seed Fund',
        'funder': 'National Science Foundation',
        'description': 'Supports translational R&D across AI, biotech, manufacturing, and more.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $2 million',
        'eligibility': 'Deep tech startups in the U.S.',
        'url': 'https://seedfund.nsf.gov/',
        'focus_areas': ['Technology', 'R&D']
    },
    {
        'title': 'Service2CEO Program',
        'funder': 'The Rosie Network',
        'description': 'Comprehensive program to help scale veteran-led businesses.',
        'deadline': 'Rolling',
        'funding_amount': 'Free curriculum, mentorship',
        'eligibility': 'Military-connected entrepreneurs.',
        'url': 'https://www.therosienetwork.org/service2ceo-program',
        'focus_areas': ['Veterans', 'Business Development']
    },
    {
        'title': 'Small Business Readiness for Resiliency Grant',
        'funder': 'U.S. Chamber of Commerce Foundation',
        'description': 'FedEx-supported initiative to boost disaster resilience.',
        'deadline': 'Rolling',
        'funding_amount': '$5,000',
        'eligibility': 'Disaster-prepared small businesses.',
        'url': 'https://www.uschamberfoundation.org/solutions/disaster-response-and-resiliency/small-business-readiness-for-resiliency',
        'focus_areas': ['Disaster Preparedness', 'Small Business']
    },
    {
        'title': 'Small Certified Supplier Innovative Finance Program',
        'funder': 'Founders First Capital Partners',
        'description': 'Helps build capacity and match suppliers with funding opportunities.',
        'deadline': 'Rolling',
        'funding_amount': '$5,000 + training',
        'eligibility': 'Certified suppliers in select states.',
        'url': 'https://www.foundersfirstcapitalpartners.com/small-certified-supplier-innovative-finance-program/',
        'focus_areas': ['Supplier Diversity', 'Small Business']
    },
    {
        'title': 'SPUR Pathways',
        'funder': 'Macy\'s and Momentus',
        'description': 'Joint initiative to fund and grow retail ventures.',
        'deadline': 'Rolling',
        'funding_amount': 'Access to capital',
        'eligibility': 'Underrepresented business owners ready for retail growth.',
        'url': 'https://www.macysinc.com/purpose/spurpathways',
        'focus_areas': ['Retail', 'Diversity']
    },
    {
        'title': 'Start Small Think Big',
        'funder': 'Start Small Think Big',
        'description': 'Offers legal, financial, and marketing help for underserved entrepreneurs.',
        'deadline': 'Rolling',
        'funding_amount': 'Free business services',
        'eligibility': '<$500 recurring sales, income under 750% FPG.',
        'url': 'https://www.startsmallthinkbig.org/events-for-small-businesses',
        'focus_areas': ['Underserved', 'Small Business']
    },
    {
        'title': 'Substack Creator Accelerator Fund',
        'funder': 'Substack',
        'description': 'Boosts subscription businesses through creator support network.',
        'deadline': 'Rolling',
        'funding_amount': 'Growth support, publishing tools',
        'eligibility': 'U.S.-based creators with $2K+ monthly revenue.',
        'url': 'https://read.substack.com/p/substack-creator-accelerator-fund',
        'focus_areas': ['Content Creation', 'Subscription Business']
    },
    {
        'title': 'This Woman Knows Grant',
        'funder': 'This Woman Knows',
        'description': 'Monthly grant for women creatives and entrepreneurs.',
        'deadline': 'Monthly',
        'funding_amount': '$500',
        'eligibility': 'U.S.-based women creatives and entrepreneurs.',
        'url': 'https://thiswomanknows.com/grant/',
        'focus_areas': ['Women-Owned', 'Creative']
    },
    {
        'title': 'Truist NonProfit Grant',
        'funder': 'Truist Foundation',
        'description': 'Foundation supports systemic impact across four core mission areas.',
        'deadline': 'Quarterly',
        'funding_amount': 'Various',
        'eligibility': 'U.S. nonprofits focused on equity, mobility, leadership.',
        'url': 'https://www.truist.com/purpose/truist-foundation/grant-application',
        'focus_areas': ['Nonprofits', 'Social Impact']
    },
    {
        'title': 'U.S. Venture/Schmidt Family Foundation Grant',
        'funder': 'U.S. Venture / Schmidt Family Foundation',
        'description': 'Wide scope including health, housing, education, and economic mobility.',
        'deadline': 'Quarterly',
        'funding_amount': 'Various',
        'eligibility': 'U.S.-based nonprofit organizations.',
        'url': 'https://www.usventure.com/giving-back/us-venture-schmidt-family-foundation/program-grants/',
        'focus_areas': ['Nonprofits', 'Community Development']
    },
    {
        'title': 'Veterans Business Outreach Center',
        'funder': 'Small Business Administration',
        'description': 'SBA-sponsored centers offering localized and virtual support.',
        'deadline': 'Rolling',
        'funding_amount': 'Mentorship, training, resources',
        'eligibility': 'Veterans interested in launching or growing a business.',
        'url': 'https://www.sba.gov/local-assistance/resource-partners/veterans-business-outreach-center-vboc-program',
        'focus_areas': ['Veterans', 'Business Development']
    },
    {
        'title': 'Warrior Rising Grant',
        'funder': 'Warrior Rising',
        'description': 'Supports veteran entrepreneurs through funding, training, and mentorship.',
        'deadline': 'Rolling',
        'funding_amount': '$20,000',
        'eligibility': 'Veterans at any stage of business.',
        'url': 'https://www.warriorrising.org/apply/',
        'focus_areas': ['Veterans', 'Entrepreneurship']
    },
    {
        'title': 'Wish Local Empowerment Program',
        'funder': 'Wish',
        'description': 'Aims to grow neighborhood-serving storefronts.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $2,000',
        'eligibility': 'Black-owned U.S. brick-and-mortar businesses (<20 employees).',
        'url': 'https://www.wish.com/local/empowerment',
        'focus_areas': ['Black-Owned', 'Retail']
    },
    {
        'title': 'YippityDoo Big Idea Grant (For-Profit)',
        'funder': 'YippityDoo',
        'description': 'Monthly grant supporting women entrepreneurs in marketing, operations, or startup needs.',
        'deadline': 'Monthly',
        'funding_amount': '$1,000',
        'eligibility': 'Women (18+) in the U.S. with a for-profit business or idea.',
        'url': 'https://www.yippitydoo.com/small-business-grant-optin/',
        'focus_areas': ['Women-Owned', 'Entrepreneurship']
    },
    {
        'title': 'YippityDoo Big Idea Grant (Non-Profit)',
        'funder': 'YippityDoo',
        'description': 'Monthly grant supporting women-led nonprofits in outreach, growth, and operations.',
        'deadline': 'Monthly',
        'funding_amount': '$1,000',
        'eligibility': 'Women (18+) in the U.S. leading or launching a nonprofit.',
        'url': 'https://www.yippitydoo.com/small-business-grant-optin-non-profit/',
        'focus_areas': ['Women-Owned', 'Nonprofits']
    },
    {
        'title': 'ZenBusiness Free LLC Formation for Moms',
        'funder': 'ZenBusiness',
        'description': 'Provides free LLC setup and business tools to help moms launch and grow businesses.',
        'deadline': 'Rolling',
        'funding_amount': 'Free LLC setup',
        'eligibility': 'Mothers in the U.S. starting or formalizing a business.',
        'url': 'https://www.zenbusiness.com/moms/',
        'focus_areas': ['Women-Owned', 'Legal Services']
    },
    {
        'title': 'RestorHER Micro-Grant',
        'funder': 'RestorHER',
        'description': 'Quarterly grant for sustainable, purpose-driven businesses prioritizing well-being.',
        'deadline': 'October 31, 2025',
        'funding_amount': 'Up to $500',
        'eligibility': 'Women business owners.',
        'url': 'https://cheyathousand.com/micro-grant',
        'focus_areas': ['Women-Owned', 'Sustainability']
    },
    {
        'title': 'Black & Brown Fund Empower Growth Grant',
        'funder': 'Black & Brown Founders',
        'description': 'Helps scale or stabilize growing businesses.',
        'deadline': 'Rolling',
        'funding_amount': '$5,000',
        'eligibility': 'Underrepresented entrepreneurs with recent revenue.',
        'url': 'https://blackandbrownfounders.com/egf',
        'focus_areas': ['Black-Owned', 'Minority-Owned']
    },
    {
        'title': 'Britt Assist Grant',
        'funder': 'Britt Assist',
        'description': 'Two awards given twice a year for small businesses.',
        'deadline': 'Rolling',
        'funding_amount': 'Free services/resources',
        'eligibility': 'Businesses earning <$175K/year.',
        'url': 'https://brittassist.com/assistfund',
        'focus_areas': ['Small Business', 'Support Services']
    },
    {
        'title': 'Creator Innovation Fund',
        'funder': 'TrendingUp',
        'description': 'Funds digital projects with social issue education focus.',
        'deadline': 'Rolling',
        'funding_amount': 'Up to $50,000',
        'eligibility': 'Content creators with social impact ideas.',
        'url': 'https://www.trendingup.org/creator-innovation-fund/',
        'focus_areas': ['Content Creation', 'Social Impact']
    },
    {
        'title': 'Entreprenista',
        'funder': 'Entreprenista',
        'description': 'Community and tools for scaling women-led businesses.',
        'deadline': 'Rolling',
        'funding_amount': 'Resources and community',
        'eligibility': 'Women entrepreneurs.',
        'url': 'https://www.entreprenista.com/newsletter',
        'focus_areas': ['Women-Owned', 'Community']
    }
]


async def populate_database():
    """Populate the grants database"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        grants_collection = db.grants
        
        print(f"Connected to database: {db_name}")
        
        # Clear existing grants
        result = await grants_collection.delete_many({})
        print(f"Cleared {result.deleted_count} existing grants")
        
        # Add timestamp and source to each grant
        for grant in GRANTS_DATA:
            grant['source'] = 'Black Tech Saturdays PDF'
            grant['date_added'] = datetime.utcnow()
            grant['is_active'] = True
        
        # Insert all grants
        result = await grants_collection.insert_many(GRANTS_DATA)
        print(f"Successfully inserted {len(result.inserted_ids)} grants")
        
        # Create indexes for better search performance
        await grants_collection.create_index([('title', 'text'), ('description', 'text'), ('focus_areas', 'text')])
        print("Created text index for search")
        
        # Display summary
        total = await grants_collection.count_documents({})
        print(f"\nTotal grants in database: {total}")
        
        client.close()
        print("Database connection closed")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(populate_database())
