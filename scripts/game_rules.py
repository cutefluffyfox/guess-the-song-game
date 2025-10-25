MAX_SUBMISSION_COUNT = 3

POSSIBLE_SUBMITTERS = sorted([
    'Ckcky’, ‘Komider’, ‘Yeo’, ‘Fluffy’, ‘Thires’, ‘Voice’, ‘SkyfallStar’, ‘Leonyardo’, ‘Potato’, ‘CocoBeansies’, ‘Laya’, ‘Wizzet’, ‘Coconaught’, ‘Ethomit’, ‘Arya’, ‘Queen’, ‘Thires’
])

POSSIBLE_AUTHORS = sorted([
    'Kn1ght', 'Glyde', 'Dad Feels', 'Exmortus', 'Metallica', 'Mariah Carrey', 'Nel Cicierega', 'Bring me the Horizon', 'Empire of a sun', 
    'Natori', 'Starset', 'Beck ft Robyn & the lonely island', 'Parov Stelar', 'Glass beach', 'Jonathan Bree', 'Jude York'
])

POSSIBLE_TITLES = sorted([
    'Something Memorable', 'Overdose', 'Cold Weather', 'Infinite', '72 Seasons', 'Catgroove', 'Moonlight Sonata', '300MB', 'You’re so cool', 
    'All I want for christmas is you', 'Can’t be stopped', 'Kingslayer', 'Super cool', 'Walking on a dream', 'Monsters', 'Those were the days'
])

# DEFAULT_IFRAME_LINK = 'https://sketchfab.com/models/befbb2c422fc4b92aecae8c5114967e9/embed?autostart=1&internal=1&tracking=0&ui_infos=0&ui_snapshots=1&ui_stop=0&ui_watermark=0'
DEFAULT_IFRAME_LINK = 'https://www.openstreetmap.org/export/embed.html?bbox=-0.004017949104309083%2C51.47612752641776%2C0.00030577182769775396%2C51.478569861898606&amp;layer=mapnik'

ADMIN_USERNAME = 'Le Voice'

TEXT_TO_EMOTE = {
    ':smile:': 'static/images/smile.webp',
    ':sadcat:': 'static/images/SadCat.png',
    ':mpreg:': 'static/images/icon.png',
    ':sus:': 'static/images/sus.png',
    ':enrichment:': 'static/images/a.gif',
    ':gopissgirl:': 'static/images/gopissgirl.webp',
    ':reallysus:': 'static/images/reallysus.webp',
    ':life:': 'static/images/life.webp',
    ':wisdom:': 'static/images/wisdom.webp',
    ':nowisdom:': 'static/images/nowisdom.webp',
    ':monksilly:': 'static/images/monksilly.webp',
    ':well:': 'static/images/well.webp',
    ':wahuh:': 'static/images/wahuh.webp',
    ':muimui:': 'static/images/muimui.webp',
    ':okak:': 'static/images/okak.webp',
    ':saussage:': 'static/images/saussage.webp',
    ':o7:': 'static/images/o7.webp',
    ':nooooo:': 'static/images/nooooo.webp',
    ':unxdd:': 'static/images/unxdd.avif',
    ':otag:': 'static/images/otag.webp',
    ':wowie:': 'static/images/wowie.webp',
    ':sobcry:': 'static/images/sobcry.png',
    ':sob:': 'static/images/sob.svg',
    ':om:': 'static/images/om.avif',
    ':loolo:': 'static/images/loolo.avif',
    ':doid:': 'static/images/doid.avif',
    ':catjam:': 'static/images/catjam.avif',
    ':yippee:': 'static/images/yippee.avif',
    ':polite:': 'static/images/polite.webp',
    ':police:': 'static/images/police.avif',
    ':modpet:': 'static/images/modpet.avif',
    ':bunjam:': 'static/images/bunjam.avif',
    ':jigglin:': 'static/images/jigglin.avif',
    ':peepofat:': 'static/images/peepofat.avif',
    ':thevoices:': 'static/images/thevoices.avif',
    ':slopslop:': 'static/images/slopslop.webp',
    ':coco:': 'static/images/coco.gif',
    ':california:': 'static/images/california-girls.gif',
    ':dance:': 'static/images/dance.gif',
    ':rat:': 'static/images/rat.gif',
}

USERNAME_COLORS = [
    # colors taken from website: https://sashamaps.net/docs/resources/20-colors/
    # '#e6194B',  # red (difficult to read)
    '#3cb44b',  # green
    '#ffe119',  # yellow
    # '#4363d8',  # blue (difficult to read)
    '#f58231',  # orange
    '#911eb4',  # purple
    '#42d4f4',  # cyan
    # '#f032e6',  # magenta (difficult to read)
    '#bfef45',  # lime
    '#fabed4',  # pink
    # '#469990',  # teal  (difficult to read)
    '#dcbeff',  # lavender
    # '#9A6324',  # brown  (difficult to read)
    '#fffac8',  # beige
    '#800000',  # maroon
    '#aaffc3',  # mint
    # '#808000',  # olive (difficult to read)
    '#ffd8b1',  # apricot
    '#000075',  # navy blue
]

SAVES_PATH = 'saves'
MAXIMUM_SAVES_AMOUNT = 10
SAVE_IDLE_INTERVAL_SECONDS = 10
