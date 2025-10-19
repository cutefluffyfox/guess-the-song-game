MAX_SUBMISSION_COUNT = 3

POSSIBLE_SUBMITTERS = sorted([
    'CuteFluffyFox', 'yeouryl', 'Voice', 'Coconought', 'Potato', 'Ehtomit', 'Komider', 'Wizzet', 'SkyfallStar', 'Laya', 'Thires', 'AryaHimself', 'CocoBeansies', 'Dweamy', 'Queen', 'CocoBeansies', 'Mask', 'Leonyardo'
])

POSSIBLE_AUTHORS = sorted([
    'Delta Goodrem', 'Camellia', 'JAMIL', 'YonKaGor', 'Aespa', 'Jamie Christopherson', 'Lovejoy', 'Kamelot', 'Vesyolye Rebyata', 'Sunrise Skater Kids', 'Mystery Skulls', 
    'Chris Christodoulou', 'Mikado', 'Hideki Naganuma', 'The scary joke', 'Mitsukiyo', 'Tyler, the creator'
])

POSSIBLE_TITLES = sorted([
    'La belette', 'Crystallised', 'The Rock City Boy', 'Believe again', 'Ain\'t nothing like a funky beat', 'Homeless Millenial', 'Darling, I', 'Linger in the rain', 
    'For the last time', 'Freaking out', 'The green letter', 'Is that me ??', 'When the lights are down', 'Coalescence', 'It has to be this way', 'Hold on tight', 'With Rob as my witness'
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
