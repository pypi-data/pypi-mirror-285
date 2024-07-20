News API
============

News API is a simple tool for scraping news data. It returns the news title, description, and more.

![Build Status](https://img.shields.io/badge/build-passing-green)
![Code Climate](https://img.shields.io/badge/maintainability-B-purple)
![Prod Ready](https://img.shields.io/badge/production-ready-blue)

This is a Python API Wrapper for the [News API](https://apiverve.com/marketplace/api/news)

---

## Installation
	pip install apiverve-news

---

## Configuration

Before using the news API client, you have to setup your account and obtain your API Key.  
You can get it by signing up at [https://apiverve.com](https://apiverve.com)

---

## Usage

The News API documentation is found here: [https://docs.apiverve.com/api/news](https://docs.apiverve.com/api/news).  
You can find parameters, example responses, and status codes documented here.

### Setup

```
# Import the client module
from apiverve_news.apiClient import NewsAPIClient

# Initialize the client with your APIVerve API key
api = NewsAPIClient("[YOUR_API_KEY]")
```

---


### Perform Request
Using the API client, you can perform requests to the API.

###### Define Query

```
query = { "category": "technology" }
```

###### Simple Request

```
# Make a request to the API
result = api.execute(query)

# Print the result
print(result)
```

###### Example Response

```
{
  "status": "ok",
  "error": null,
  "data": {
    "date": "2024-07-17",
    "category": "technology",
    "articleCount": 60,
    "articles": [
      {
        "category": "technology",
        "website": "Latest news",
        "title": "165+ best Prime Day deals: Sales on AirPods, Kindles, Fire TV Sticks, and more",
        "pubDate": "Wed, 17 Jul 2024 15:10:31 +0000",
        "description": "Our experts found the best deals during Amazon Prime Day 2, including Apple products, TVs, laptops, headphones, robot vacuums, and more.",
        "link": "https://www.zdnet.com/article/best-amazon-prime-day-deals-live-2024-07-17/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "The 39 best Prime Day monitor deals",
        "pubDate": "Wed, 17 Jul 2024 15:08:00 +0000",
        "description": "Looking to upgrade your existing PC monitor? There are some great monitor deals from Samsung, LG, Acer, and more available during Amazon Prime Day.",
        "link": "https://www.zdnet.com/article/best-amazon-prime-day-monitor-deals-2024-07-17/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "The best budget robot vacuums",
        "pubDate": "2024-07-17T15:06:57Z",
        "description": "Illustration: The Verge          \t\t  You don’t have to spend a fortune to have a robot clean your floors. Here’s our pick of the most cost-effective bots you can buy right now. Continue reading…",
        "link": "https://www.theverge.com/23846479/best-budget-robot-vacuum-robot-mop"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "The best Prime Day deals on Amazon devices ",
        "pubDate": "2024-07-17T15:06:34Z",
        "description": "The Kindle Scribe is down to an all-time low price. | Image: Amelia Holowaty Krales          Amazon Prime Day 2024 has officially arrived. We’ve already published a detailed guide to the best Prime Day deals, but if you’re just interested in Amazon devices, this is where you’ll find the ones that are actually worthwhile. From Alexa-based Echo smart speakers to video doorbells, Amazon is discounting a wide range of gadgets, some of which are currently seeing their lowest prices to date.     Of course, the main caveat here is that you’ll have to be an active Amazon Prime member to take advantage of any and all Prime Day deals. Luckily, Amazon makes it pretty easy to sign up, especially since new members can take advantage of the exclusive discounts with a free 30-day trial.   The best streaming device and TV deals     If you’re... Continue reading…",
        "link": "https://www.theverge.com/24186875/amazon-prime-day-device-deals-echo-speakers-kindles-fire-tv-streaming-sticks-sale-2024"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "40 of the best Prime Day impulse buys you don't want to miss",
        "pubDate": "Wed, 17 Jul 2024 15:06:00 +0000",
        "description": "Get ready to dive into day two of Amazon Prime Day deals, with a raft of impulse buys and random odds-and-ends tech deals that will have you reaching for your wallet.",
        "link": "https://www.zdnet.com/home-and-office/best-prime-day-impulse-buy-deals-2024-07-17/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "The 42 best Prime Day 2024 Nintendo Switch deals",
        "pubDate": "Wed, 17 Jul 2024 15:02:00 +0000",
        "description": "It's day two of Amazon Prime Day 2024 is in full swing, and Amazon, Best Buy, and Walmart are offering great discounts on Nintendo Switch consoles, games, and accessories right now.",
        "link": "https://www.zdnet.com/home-and-office/home-entertainment/best-prime-day-nintendo-switch-deals-2024-07-17/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "Microsoft’s Designer app arrives on iOS and Android with AI editing and creation",
        "pubDate": "2024-07-17T15:00:00Z",
        "description": "Image: Microsoft          Microsoft’s AI-powered Designer app is coming out of preview today for both iOS and Android users. Microsoft Designer lets you use templates to create custom images, stickers, greeting cards, invitations, and more. Designer can also use AI to edit images and restyle them or create collages of images. Originally available on the web or through Microsoft Edge, Designer has been in preview for nearly a year. It’s now generally available to anyone with a personal Microsoft account and as a free app for Windows, iOS, and Android. The mobile app includes the ability to create images and edit them on the go. Image: Microsoft       The Microsoft Designer editor view.    Microsoft Designer includes the usual text prompt for... Continue reading…",
        "link": "https://www.theverge.com/2024/7/17/24200294/microsoft-designer-app-launch-windows-ios-android-features"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "Cadillac is giving its gas-powered Escalade an EV glow-up",
        "pubDate": "2024-07-17T15:00:00Z",
        "description": "Image: Cadillac          The Cadillac Escalade IQ, the electric version of the automaker’s yacht-sized luxury SUV, won’t be out until later this year, so in the meantime, the automaker is hoping to whet appetites by giving the gas-powered version an EV makeover. Starting the front grille, the new 2025 Escalade will have new vertically positioned headlights inspired by the Cadillac Lyriq and Celestiq, as well as an illuminated Cadillac badge in the center. And on the V-series, Premium Luxury, and Platinum trims, there is also an LED border that outlines the grille — which also calls to mind the illuminated grilles of Cadillac’s EV lineup. Moving inside, the interior has been totally redesigned to give over a lot more real estate to screens. The Escalade will now... Continue reading…",
        "link": "https://www.theverge.com/2024/7/17/24198989/cadillac-escalade-refresh-2025-screen-ev-power-doors"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "You can trade in old electronics for Amazon gift cards. Here's how it works",
        "pubDate": "Wed, 17 Jul 2024 15:00:00 +0000",
        "description": "In time for Prime Day, follow these steps to turn your unused gadgets and gizmos into Amazon gift cards.",
        "link": "https://www.zdnet.com/article/you-can-trade-in-old-electronics-for-amazon-gift-cards-heres-how-it-works/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "The best Prime Day gaming deals",
        "pubDate": "2024-07-17T14:59:04Z",
        "description": "You can get a refurbished Xbox Series X for well under $400 today — if you don’t mind buying refurbished. | Photo by Vjeran Pavic / The Verge          If you’ve worked hard this year, you deserve to play even harder, and you can do that on a modest budget with some of the Prime Day gaming deals available right now. Amazon’s Prime Day 2024 sale runs through the end of today, July 17th, offering plenty of discounts on video games, controllers, headsets, storage, and other gear and accessories to level up your experience.   We’re seeing new all-time low prices on some of the top games that have been released over the past couple of years. There’s a healthy assortment of titles to consider, whether you’re playing on PlayStation 5, Nintendo Switch, or Xbox Series X / S. There’s also quite a few deals for actual hardware, too — though no consoles apart from the Meta Quest 3 as of now. We’ll... Continue reading…",
        "link": "https://www.theverge.com/24198226/amazon-prime-day-2024-best-gaming-deals-controller-headset-accessories"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "The 18 best Prime Day Samsung phone deals",
        "pubDate": "Wed, 17 Jul 2024 14:55:00 +0000",
        "description": "The second day of Amazon Prime Day is here, and you can take advantage of deals on Samsung products, including Galaxy phones, TVs, and smart home gadgets.",
        "link": "https://www.zdnet.com/home-and-office/best-amazon-prime-day-samsung-phone-deals-2024-07-17/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "The 109 best Prime Day 2024 gaming deals",
        "pubDate": "Wed, 17 Jul 2024 14:52:00 +0000",
        "description": "Day 2 of Amazon's annual Prime Day sale is well underway, and you can find great deals on gaming consoles, PCs and laptops, accessories, and even games themselves. Hurry before these deals disappear -- Prime Day ends tonight at midnight.",
        "link": "https://www.zdnet.com/home-and-office/home-entertainment/best-amazon-prime-day-gaming-deals-2024-07-17/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "I love this DeWalt cordless drill and impact driver set, and it's 42% off for Prime Day",
        "pubDate": "Wed, 17 Jul 2024 14:49:12 +0000",
        "description": "Save $100 on this DeWalt power tool kit in this Amazon Prime Day deal before it disappears.",
        "link": "https://www.zdnet.com/home-and-office/i-love-this-dewalt-cordless-drill-and-impact-driver-set-and-its-42-off-for-prime-day/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "The Oura Ring is finally on sale through Prime Day (and that rarely happens)",
        "pubDate": "Wed, 17 Jul 2024 14:47:20 +0000",
        "description": "The Horizon Oura Ring is up $67 off during Prime Day, a rare discount on a product that rarely goes on sale.",
        "link": "https://www.zdnet.com/article/oura-ring-prime-day-sale-07-17-2024/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "Latest news",
        "title": "This Oura Ring rival is $55 off during Prime Day -- no subscription necessary",
        "pubDate": "Wed, 17 Jul 2024 14:46:35 +0000",
        "description": "The Ultrahuman Ring Air is a subscription-free smart ring that rivals the Oura Ring, and it's less than $300 on the second day of Prime Day.",
        "link": "https://www.zdnet.com/article/ultrahuman-ring-air-amazon-prime-day-deal-07-17-2024/#ftag=RSSbaffb68"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "The UK will start feeding lab-grown meat to pets this year",
        "pubDate": "2024-07-17T14:43:39Z",
        "description": "Image: Meatly          The UK is now the first European country to green-light the sale of lab-grown meat, but with pets instead of human consumers as its first guinea pigs.  The UK’s Animal and Plant Health Agency and the Department for Environment, Food & Rural Affairs granted London-based startup Meatly regulatory approval to produce lab-grown pet food, which described the clearance as a “huge leap forward for the cultivated meat industry.” “Pet parents are crying out for a better way to feed their cats and dogs meat,” Meatly CEO Owen Ensor said in a statement, pitching that the company’s cultivated pet food would allow them to do so “in a way that is kinder to our planet and other animals.”  Meatly says it plans to launch commercial samples of its first... Continue reading…",
        "link": "https://www.theverge.com/2024/7/17/24200412/uk-lab-grown-cultivated-meat-pet-food-approval-meatly"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "The Fitbit Charge 6 Is a Deal at Just $100 Right Now",
        "pubDate": "Wed, 17 Jul 2024 14:31:00 +0000",
        "description": "The best fitness tracker you can buy—at its best price. Can we get a W in the chat?",
        "link": "https://www.wired.com/story/fitbit-charge-6-prime-day-deal/"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "The best Apple deals available for Amazon Prime Day 2024 ",
        "pubDate": "2024-07-17T14:30:30Z",
        "description": "The latest iPad is down to an all-time low price. | Photo by Dan Seifert / The Verge          Thanks to Amazon Prime Day, you don’t need to wait until Black Friday this year to save big on Apple gadgets. Despite being an Amazon event, some of the best deals surprisingly include popular Apple products, ranging from the high-end latest AirPods Pro to the entry-level third-gen AirPods — both of which have new all-time low prices.    It’s not just AirPods that are receiving steep discounts, though, but also the Apple Watch Series 9, the latest iPad, and other excellent Apple devices. Below, we’ve rounded up the cream of the crop to make diving through the deals easier. If you’re interested in deals outside of the Apple ecosystem, check out our main Prime Day roundup so you can save even more. The best AirPods deals    Normally $549.99,...     Continue reading…",
        "link": "https://www.theverge.com/24196778/amazon-prime-day-apple-deals-airpods-watch-ipad-macbook-2024"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "6 Best Amazon Prime Day Coffee Deals",
        "pubDate": "Wed, 17 Jul 2024 14:18:07 +0000",
        "description": "Get wired with these piping-hot Prime Day coffee deals on espresso machines, grinders, and coffee beans.",
        "link": "https://www.wired.com/story/prime-day-coffee-deals-2024-1/"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "How Trump’s Running Mate J.D. Vance is Connected to Silicon Valley",
        "pubDate": "Wed, 17 Jul 2024 14:13:10 +0000",
        "description": "Mr. Vance spent less than five years in Silicon Valley’s tech industry, but the connections he made with Peter Thiel and others became crucial to his political ascent.",
        "link": "https://www.nytimes.com/2024/07/17/technology/jd-vance-tech-silicon-valley.html"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Windows 11 24H2 update may not turn up until late in the year – and given how many plates Microsoft is spinning, that wouldn’t surprise us ",
        "pubDate": "Wed, 17 Jul 2024 14:11:57 +0000",
        "description": "Can’t wait for the big 24H2 update? Well, you might have to, and we can readily believe the upgrade could be delayed.",
        "link": "https://www.techradar.com/computing/windows/windows-11-24h2-update-may-not-turn-up-until-late-in-the-year-and-given-how-many-plates-microsoft-is-spinning-that-wouldnt-surprise-us"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "OpenAI CEO Sam Altman’s $27 million mansion is a ‘lemon’ with a leaky pool, lawsuit alleges",
        "pubDate": "2024-07-17T14:11:01Z",
        "description": "Image: Cath Virginia / The Verge; Getty Images          Sam Altman’s $27 million San Francisco luxury abode is apparently plagued with issues, ranging from a leaky infinity pool to faulty piping that dumped raw sewage on the property. That’s according to a lawsuit that The San Francisco Standard linked to the OpenAI CEO’s residence, which claims Altman purchased a “lemon” with “pervasive shoddy workmanship and corner-cutting.” The 9,500-square-foot estate is situated on San Francisco’s iconic Lombard Street, where it overlooks the city and the bay. As you can see in this walkthrough of the home, some of its key features include a four-sided infinity pool that hangs off the edge of the house, a “Batcave” leading into a garage, as well as a system that uses recycled rainwater to irrigate an... Continue reading…",
        "link": "https://www.theverge.com/2024/7/17/24200354/sam-altman-san-francisco-mansion-lawsuit-lemon-openai"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "Home Depot’s viral giant skeleton has some upgrades — and lots of new friends",
        "pubDate": "2024-07-17T14:02:53Z",
        "description": "Image: Home Depot          Five years ago, Home Depot stumbled upon a viral hit with a 12-foot-tall skeleton nicknamed Skelly. The towering Halloween decoration can be seen year-round in some neighborhoods, has been featured in countless memes and TikToks, and remains a hot ticket — it went back on sale in April and promptly sold out. Now the company is bringing back a slightly refreshed version of the skeleton as part of a huge lineup of Halloween creatures packed with LEDs and animatronics, as it looks to keep its undead hit alive. Skelly remains the centerpiece. The skeleton is going back on sale with a slight tweak: now those creepy LED eyes are customizable, with eight different presets so you can keep Skelly in style for multiple holidays. One of the options... Continue reading…",
        "link": "https://www.theverge.com/2024/7/17/24199821/home-depot-halloween-2024-skelly-skeleton"
      },
      {
        "category": "technology",
        "website": "The Verge -  All Posts",
        "title": "The best Prime Day deals on smart home gear",
        "pubDate": "2024-07-17T14:00:00Z",
        "description": "The Blink Video Doorbell is down to $30 for Prime Day. | Photo by Jennifer Pattison Tuohy / The Verge          Amazon’s Prime Day 2024 runs from Tuesday, July 16th, through Wednesday, July 17th, and is an excellent way to stock up on smart home gear. I spent hours sifting through the best deals to bring you my picks for the best buys. Grab some serious bargains on robot vacuums, smart kitchen gadgets, and lots of smart plugs. Plus, smart lighting favorites Philips Hue and Lutron Caséta have some select savings on their popular products. Read on for all the latest deals, and be sure to check back, as I’ll keep this updated throughout the sale.    Best deals on Amazon Echo devices Several of my favorite Echo smart speakers and displays are on sale this Prime Day. If you’re looking for good sound and a smart home hub that adds support for T...  Continue reading…",
        "link": "https://www.theverge.com/2024/7/16/24199019/amazon-prime-day-best-smart-home-deals-robot-vacuums-video-doorbells-smart-bulbs"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "WIRED's Top Prime Day Deals on Wires, Cords, and Cables So You Can Stay Wired Forever (2024)",
        "pubDate": "Wed, 17 Jul 2024 13:53:05 +0000",
        "description": "The humble cable is a necessity for our tech gadgets, and these Prime Day deals will keep you wired.",
        "link": "https://www.wired.com/story/amazon-prime-day-cables-deals-2024/"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "The New UK Government Wants Clean Energy, Sustainable Aviation Fuel, and Public Transport Reform",
        "pubDate": "Wed, 17 Jul 2024 13:10:36 +0000",
        "description": "Legislation in coming years will set up a publicly owned clean power company and leverage the Crown Estate for investment in green infrastructure.",
        "link": "https://www.wired.com/story/kings-speech-starmer-labour-climate-environment-policy/"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "Best Prime Day Toy Deals on Board Games and Legos (2024)",
        "pubDate": "Wed, 17 Jul 2024 12:57:25 +0000",
        "description": "Play around with these Amazon Prime Day deals on some of our favorite toys and board games.",
        "link": "https://www.wired.com/story/amazon-prime-day-toy-game-deals-1/"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "The Race for Space-Based Solar Power",
        "pubDate": "Wed, 17 Jul 2024 12:00:00 +0000",
        "description": "Once a sci-fi staple, the ability to beam solar power from space now seems closer than ever—but a lot of work remains.",
        "link": "https://www.wired.com/story/sun-based-solar-power-esa-energy/"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Intel raising power safeguard for next-gen Arrow Lake CPUs has rung alarm bells for some – but we’re hopeful it’s a positive sign ",
        "pubDate": "Wed, 17 Jul 2024 11:56:34 +0000",
        "description": "Will Intel’s next-gen processors put Core i9 stability issues firmly in the rearview mirror?",
        "link": "https://www.techradar.com/computing/cpu/intel-raising-power-safeguard-for-next-gen-arrow-lake-cpus-has-rung-alarm-bells-for-some-but-were-hopeful-its-a-positive-sign"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "The Best Prime Day Gaming Deals You Don't Want to Miss (2024)",
        "pubDate": "Wed, 17 Jul 2024 11:54:33 +0000",
        "description": "Amazon’s Prime Day event is packed with deals for gamers on everything from OLED gaming monitors to gaming keyboards and controllers. Oh, and games too!",
        "link": "https://www.wired.com/story/amazon-prime-day-gaming-deals-2024/"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "The Paris Olympics Will Show Us the Future of Sports on TV",
        "pubDate": "Wed, 17 Jul 2024 11:30:00 +0000",
        "description": "This summer’s Games are going to look bigger and better and louder than ever, thanks to key innovations in the broadcast booth and in the cloud.",
        "link": "https://www.wired.com/story/paris-olympics-broadcast-tech-ai/"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "The Top 5 Prime Day Kindle Deals—Plus More Amazon Devices (2024)",
        "pubDate": "Wed, 17 Jul 2024 11:10:44 +0000",
        "description": "Amazon's shopping holiday is the best time to buy some of the brand's devices that we love.",
        "link": "https://www.wired.com/story/prime-day-kindle-amazon-device-deals-2024-1/"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Navigating Insider Risks: Are your Employees Enabling External Threats?",
        "pubDate": "Wed, 17 Jul 2024 16:39:00 +0530",
        "description": "Attacks on your network are often meticulously planned operations launched by sophisticated threats. Sometimes your technical fortifications provide a formidable challenge, and the attack requires assistance from the inside to succeed. For example, in 2022, the FBI issued a warning1 that SIM swap attacks are growing: gain control of the phone and earn a gateway to email, bank accounts, stocks,",
        "link": "https://thehackernews.com/2024/07/navigating-insider-risks-are-your.html"
      },
      {
        "category": "technology",
        "website": "Wired",
        "title": "RealPage Says Rental Pricing Tech Is Misunderstood, but Landlords Aren’t So Sure",
        "pubDate": "Wed, 17 Jul 2024 11:01:50 +0000",
        "description": "The software company has pushed back hard against claims that its algorithms helped make rent in the US too damn high. Property owners and managers aren't entirely convinced.",
        "link": "https://www.wired.com/story/realpage-says-rental-pricing-tech-is-misunderstood-but-landlords-arent-so-sure/"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " The Meta Quest 3’s Netflix app has been shut for good – but the alternative is better than it ever was ",
        "pubDate": "Wed, 17 Jul 2024 10:46:09 +0000",
        "description": "Netflix's Meta Quest browser experience is better than the app ever was, but it's still a flawed system.",
        "link": "https://www.techradar.com/computing/virtual-reality-augmented-reality/the-meta-quest-3s-netflix-app-has-been-shut-for-good-but-the-alternative-is-better-than-it-ever-was"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "FIN7 Group Advertises Security-Bypassing Tool on Dark Web Forums",
        "pubDate": "Wed, 17 Jul 2024 16:03:00 +0530",
        "description": "The financially motivated threat actor known as FIN7 has been observed using multiple pseudonyms across several underground forums to likely advertise a tool known to be used by ransomware groups like Black Basta. \"AvNeutralizer (aka AuKill), a highly specialized tool developed by FIN7 to tamper with security solutions, has been marketed in the criminal underground and used by multiple",
        "link": "https://thehackernews.com/2024/07/fin7-group-advertises-security.html"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Believe it or not, AMD has already begun work on Zen 7 CPUs that are three generations into the future ",
        "pubDate": "Wed, 17 Jul 2024 09:45:32 +0000",
        "description": "Excited about Ryzen 9000 CPUs? Forget them, AMD is already working on Zen 7 chips that won’t arrive until 2028.",
        "link": "https://www.techradar.com/computing/cpu/believe-it-or-not-amd-has-already-begun-work-on-zen-7-cpus-that-are-three-generations-into-the-future"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "China-linked APT17 Targets Italian Companies with 9002 RAT Malware",
        "pubDate": "Wed, 17 Jul 2024 14:17:00 +0530",
        "description": "A China-linked threat actor called APT17 has been observed targeting Italian companies and government entities using a variant of a known malware referred to as 9002 RAT. The two targeted attacks took place on June 24 and July 2, 2024, Italian cybersecurity company TG Soft said in an analysis published last week. \"The first campaign on June 24, 2024 used an Office document, while the second",
        "link": "https://thehackernews.com/2024/07/china-linked-apt17-targets-italian.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Scattered Spider Adopts RansomHub and Qilin Ransomware for Cyber Attacks",
        "pubDate": "Wed, 17 Jul 2024 11:20:00 +0530",
        "description": "The infamous cybercrime group known as Scattered Spider has incorporated ransomware strains such as RansomHub and Qilin into its arsenal, Microsoft has revealed. Scattered Spider is the designation given to a threat actor that's known for its sophisticated social engineering schemes to breach targets and establish persistence for follow-on exploitation and data theft. It also has a history of",
        "link": "https://thehackernews.com/2024/07/scattered-spider-adopts-ransomhub-and.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Critical Apache HugeGraph Vulnerability Under Attack - Patch ASAP",
        "pubDate": "Wed, 17 Jul 2024 10:55:00 +0530",
        "description": "Threat actors are actively exploiting a recently disclosed critical security flaw impacting Apache HugeGraph-Server that could lead to remote code execution attacks. Tracked as CVE-2024-27348 (CVSS score: 9.8), the vulnerability impacts all versions of the software before 1.3.0. It has been described as a remote command execution flaw in the Gremlin graph traversal language API. \"Users are",
        "link": "https://thehackernews.com/2024/07/critical-apache-hugegraph-vulnerability.html"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Claude AI is now on Android where it could dethrone ChatGPT as the most secure AI app ",
        "pubDate": "Wed, 17 Jul 2024 05:00:41 +0000",
        "description": "Claude AI gives Android owners a more secure way to answer all your burning questions and solve those tough problems.",
        "link": "https://www.techradar.com/computing/artificial-intelligence/claude-ai-is-now-on-android-where-it-could-dethrone-chatgpt-as-the-most-secure-ai-app"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "Elon Musk Says He Will Move X and SpaceX Headquarters to Texas",
        "pubDate": "Wed, 17 Jul 2024 00:37:16 +0000",
        "description": "The social media and rocket companies are based in California, which the billionaire criticized for its recent transgender legislation.",
        "link": "https://www.nytimes.com/2024/07/16/technology/elon-musk-x-spacex-headquarters-texas.html"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " NYT Strands today — hints, answers and spangram for Wednesday, July 17 (game #136) ",
        "pubDate": "Tue, 16 Jul 2024 23:02:00 +0000",
        "description": "Looking for NYT Strands answers and hints? Here's all you need to know to solve today's game, including the spangram.",
        "link": "https://www.techradar.com/computing/websites-apps/nyt-strands-today-answers-hints-17-july-2024"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Quordle today – hints and answers for Wednesday, July 17 (game #905) ",
        "pubDate": "Tue, 16 Jul 2024 23:02:00 +0000",
        "description": "Looking for Quordle clues? We can help. Plus get the answers to Quordle today and past solutions.",
        "link": "https://www.techradar.com/computing/websites-apps/quordle-today-answers-clues-17-july-2024"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Investigation finds companies are training AI models with YouTube content without permission ",
        "pubDate": "Tue, 16 Jul 2024 22:30:15 +0000",
        "description": "YouTube data is being used without asking creators to train AI models.",
        "link": "https://www.techradar.com/computing/artificial-intelligence/investigation-finds-companies-are-training-ai-models-with-youtube-content-without-permission"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "Is It Silicon Valley’s Job to Make Guaranteed Income a Reality?",
        "pubDate": "Tue, 16 Jul 2024 19:20:11 +0000",
        "description": "The tech community, led by Sam Altman of OpenAI, has funded programs that give people unconditional cash. Some say it’s time to scale up.",
        "link": "https://www.nytimes.com/2024/07/16/technology/ubi-openai-silicon-valley.html"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " Xreal's Beam Pro is a new cheap spatial computer doesn't quite stick the landing ",
        "pubDate": "Tue, 16 Jul 2024 19:00:38 +0000",
        "description": "The Xreal Beam Pro delivers a solid portable TV experience, but it's not yet the spatial computer we need it to be.",
        "link": "https://www.techradar.com/computing/virtual-reality-augmented-reality/xreals-beam-pro-is-a-new-cheap-spatial-computer-doesnt-quite-stick-the-landing"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "How Microsoft’s Satya Nadella Became Tech’s Steely Eyed A.I. Gambler",
        "pubDate": "Tue, 16 Jul 2024 15:05:23 +0000",
        "description": "Microsoft’s all-in moment on artificial intelligence has been defined by billions in spending and a C.E.O. counting on technology with huge potential and huge risks.",
        "link": "https://www.nytimes.com/2024/07/14/technology/microsoft-ai-satya-nadella.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "'Konfety' Ad Fraud Uses 250+ Google Play Decoy Apps to Hide Malicious Twins",
        "pubDate": "Tue, 16 Jul 2024 18:30:00 +0530",
        "description": "Details have emerged about a \"massive ad fraud operation\" that leverages hundreds of apps on the Google Play Store to perform a host of nefarious activities. The campaign has been codenamed Konfety – the Russian word for Candy – owing to its abuse of a mobile advertising software development kit (SDK) associated with a Russia-based ad network called CaramelAds. \"Konfety represents a new form of",
        "link": "https://thehackernews.com/2024/07/konfety-ad-fraud-uses-250-google-play.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Threat Prevention & Detection in SaaS Environments - 101",
        "pubDate": "Tue, 16 Jul 2024 16:30:00 +0530",
        "description": "Identity-based threats on SaaS applications are a growing concern among security professionals, although few have the capabilities to detect and respond to them.  According to the US Cybersecurity and Infrastructure Security Agency (CISA), 90% of all cyberattacks begin with phishing, an identity-based threat. Throw in attacks that use stolen credentials, over-provisioned accounts, and",
        "link": "https://thehackernews.com/2024/07/threat-prevention-detection-in-saas.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Malicious npm Packages Found Using Image Files to Hide Backdoor Code",
        "pubDate": "Tue, 16 Jul 2024 15:39:00 +0530",
        "description": "Cybersecurity researchers have identified two malicious packages on the npm package registry that concealed backdoor code to execute malicious commands sent from a remote server. The packages in question – img-aws-s3-object-multipart-copy and legacyaws-s3-object-multipart-copy – have been downloaded 190 and 48 times each. As of writing, they have been taken down by the npm security team. \"They",
        "link": "https://thehackernews.com/2024/07/malicious-npm-packages-found-using.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Iranian Hackers Deploy New BugSleep Backdoor in Middle East Cyber Attacks",
        "pubDate": "Tue, 16 Jul 2024 14:43:00 +0530",
        "description": "The Iranian nation-state actor known as MuddyWater has been observed using a never-before-seen backdoor as part of a recent attack campaign, shifting away from its well-known tactic of deploying legitimate remote monitoring and management (RMM) software for maintaining persistent access. That's according to independent findings from cybersecurity firms Check Point and Sekoia, which have",
        "link": "https://thehackernews.com/2024/07/iranian-hackers-deploy-new-bugsleep.html"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "Elon Musk Enters Uncharted Territory With Trump Endorsement",
        "pubDate": "Tue, 16 Jul 2024 09:03:54 +0000",
        "description": "The owner of X broke with tradition at other social media companies to support the former president, as he drives political conversation on his site.",
        "link": "https://www.nytimes.com/2024/07/16/technology/elon-musk-trump.html"
      },
      {
        "category": "technology",
        "website": "The Hacker News",
        "title": "Void Banshee APT Exploits Microsoft MHTML Flaw to Spread Atlantida Stealer",
        "pubDate": "Tue, 16 Jul 2024 14:30:00 +0530",
        "description": "An advanced persistent threat (APT) group called Void Banshee has been observed exploiting a recently disclosed security flaw in the Microsoft MHTML browser engine as a zero-day to deliver an information stealer called Atlantida. Cybersecurity firm Trend Micro, which observed the activity in mid-May 2024, the vulnerability – tracked as CVE-2024-38112 – was used as part of a multi-stage attack",
        "link": "https://thehackernews.com/2024/07/void-banshee-apt-exploits-microsoft.html"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "Donald Trump Was Shot. Then the Conspiracy Theories Spread.",
        "pubDate": "Mon, 15 Jul 2024 22:14:47 +0000",
        "description": "Claims that President Biden and his allies ordered the attack on Donald J. Trump, or that Mr. Trump staged the attack, started quickly and spread fast across social media.",
        "link": "https://www.nytimes.com/2024/07/15/technology/trump-shooting-conspiracy-theories.html"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "Electric Vehicles May Become Harder to Rent",
        "pubDate": "Mon, 15 Jul 2024 19:30:03 +0000",
        "description": "Rental car firms are offering temporary deals on electric cars, which they are selling after they lost value more quickly than expected.",
        "link": "https://www.nytimes.com/2024/07/14/business/electric-vehicles-rental-cars.html"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "Google Close to Its Biggest Acquisition Ever, Despite Antitrust Scrutiny",
        "pubDate": "Mon, 15 Jul 2024 18:31:38 +0000",
        "description": "The search giant’s negotiations to buy Wiz, a cybersecurity start-up, for $23 billion, come as the Biden administration has taken a hard line against consolidation in tech and other industries.",
        "link": "https://www.nytimes.com/2024/07/14/technology/google-wiz-deal.html"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "A Reporter Who Sees Meaning in the Stars",
        "pubDate": "Sun, 14 Jul 2024 07:00:18 +0000",
        "description": "As a science reporter, Katrina Miller covers the cosmos, innovations in physics, space exploration and more.",
        "link": "https://www.nytimes.com/2024/07/14/insider/space-reporting.html"
      },
      {
        "category": "technology",
        "website": "NYT > Technology",
        "title": "The End of the Affair? Not for Eric Schmidt.",
        "pubDate": "Fri, 12 Jul 2024 17:26:01 +0000",
        "description": "While Mr. Schmidt was chief executive of Google, he had an extramarital relationship with Marcy Simon, a public relations executive. A decade after they split, things are still messy.",
        "link": "https://www.nytimes.com/2024/07/12/technology/eric-schmidt-affair.html"
      },
      {
        "category": "technology",
        "website": " TechRadar - All the latest technology news ",
        "title": " NYT Wordle today — answer and hints for game #1124, Wednesday, July 17 ",
        "pubDate": "Tue, 14 Feb 2023 09:56:57 +0000",
        "description": "Looking for Wordle hints? We can help. Plus get the answers to Wordle today and yesterday.",
        "link": "https://www.techradar.com/news/wordle-today"
      }
    ]
  }
}
```

---

## Customer Support

Need any assistance? [Get in touch with Customer Support](https://apiverve.com/contact).

---

## Updates
Stay up to date by following [@apiverveHQ](https://twitter.com/apiverveHQ) on Twitter.

---

## Legal

All usage of the APIVerve website, API, and services is subject to the [APIVerve Terms of Service](https://apiverve.com/terms) and all legal documents and agreements.

---

## License
Licensed under the The MIT License (MIT)

Copyright (&copy;) 2024 APIVerve, and Evlar LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.